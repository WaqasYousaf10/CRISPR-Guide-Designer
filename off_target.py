"""
Off-target prediction module for CRISPR guides
Uses BLAST-like approach with mismatch tolerance
"""

import re
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq


class OffTargetAnalyzer:
    """Analyze potential off-target effects of guide RNAs"""
    
    def __init__(self, genome: Optional[str] = None, max_mismatches: int = 4):
        """
        Initialize off-target analyzer
        
        Args:
            genome: Reference genome sequence
            max_mismatches: Maximum mismatches allowed for off-target identification
        """
        self.genome = genome
        self.max_mismatches = max_mismatches
        
        # Scoring weights for mismatches based on position
        # Positions closer to PAM are more important
        self.position_weights = self._generate_position_weights()
        
    def _generate_position_weights(self) -> List[float]:
        """Generate position-specific weights for mismatch scoring"""
        # PAM-proximal positions (positions 1-3 are closest to PAM)
        weights = []
        for i in range(20):
            # More weight near PAM (positions 17-19)
            if i >= 17:
                weight = 1.0
            elif i >= 14:
                weight = 0.8
            elif i >= 10:
                weight = 0.6
            elif i >= 5:
                weight = 0.4
            else:
                weight = 0.2
            weights.append(weight)
        return weights
    
    def find_off_targets(self, guide: str, genome: str, max_mismatches: int = None) -> List[Dict]:
        """
        Find potential off-target sites in genome
        
        Args:
            guide: Guide sequence (spacer only, no PAM)
            genome: Genome sequence to search
            max_mismatches: Maximum mismatches to consider
            
        Returns:
            List of off-target sites with details
        """
        if max_mismatches is None:
            max_mismatches = self.max_mismatches
            
        guide = guide.upper()
        genome = genome.upper()
        off_targets = []
        
        # Simple sliding window search
        window_size = len(guide)
        
        for i in range(len(genome) - window_size + 1):
            window = genome[i:i+window_size]
            mismatches = self._count_mismatches(guide, window)
            
            if 0 < mismatches <= max_mismatches:
                # Calculate off-target score
                score = self._calculate_offtarget_score(guide, window)
                
                off_targets.append({
                    'position': i,
                    'sequence': window,
                    'mismatches': mismatches,
                    'mismatch_positions': self._get_mismatch_positions(guide, window),
                    'score': score,
                    'severity': self._classify_severity(mismatches, score)
                })
        
        return off_targets
    
    def _count_mismatches(self, seq1: str, seq2: str) -> int:
        """Count mismatches between two sequences"""
        return sum(1 for a, b in zip(seq1, seq2) if a != b)
    
    def _get_mismatch_positions(self, seq1: str, seq2: str) -> List[int]:
        """Get positions where sequences differ"""
        return [i for i, (a, b) in enumerate(zip(seq1, seq2)) if a != b]
    
    def _calculate_offtarget_score(self, guide: str, target: str) -> float:
        """
        Calculate off-target score using position-specific weights
        
        Higher score = more likely to be a real off-target site
        """
        total_score = 0
        
        for i, (g, t) in enumerate(zip(guide, target)):
            if g != t:
                # Mismatch penalty based on position
                weight = self.position_weights[i]
                total_score += weight
        
        # Normalize score
        max_possible = sum(self.position_weights)
        score = 1 - (total_score / max_possible)
        
        return score
    
    def _classify_severity(self, mismatches: int, score: float) -> str:
        """Classify off-target severity"""
        if mismatches == 0:
            return "Perfect match (on-target)"
        elif mismatches <= 2 and score > 0.8:
            return "High risk"
        elif mismatches <= 3 and score > 0.6:
            return "Medium risk"
        else:
            return "Low risk"
    
    def analyze_guide(self, guide: str, genome: str, max_mismatches: int = 4) -> pd.DataFrame:
        """
        Comprehensive off-target analysis returning DataFrame
        
        Args:
            guide: Guide sequence (spacer only)
            genome: Reference genome
            max_mismatches: Maximum mismatches to search
            
        Returns:
            DataFrame with off-target sites
        """
        off_targets = self.find_off_targets(guide, genome, max_mismatches)
        
        if not off_targets:
            return pd.DataFrame()
        
        df = pd.DataFrame(off_targets)
        
        # Add additional metrics
        df['guide'] = guide
        df['mismatch_rate'] = (df['mismatches'] / len(guide) * 100).round(1)
        
        # Calculate cumulative off-target risk
        df['risk_score'] = df['score'] * (1 - df['mismatches'] / len(guide))
        
        return df


class GuideValidator:
    """Validate guide sequences and provide warnings"""
    
    @staticmethod
    def check_quality(guide: str) -> Dict:
        """
        Comprehensive guide quality check
        
        Returns:
            Dictionary with quality metrics and warnings
        """
        warnings = []
        metrics = {}
        
        # GC content
        gc = (guide.count('G') + guide.count('C')) / len(guide)
        metrics['gc_content'] = gc
        
        if gc < 0.3:
            warnings.append("Low GC content (<30%)")
        elif gc > 0.7:
            warnings.append("High GC content (>70%)")
        
        # Poly-T
        if 'TTTT' in guide:
            warnings.append("Contains poly-T run (risk of transcription termination)")
        
        # Poly-G
        if 'GGGG' in guide:
            warnings.append("Contains poly-G run (possible G-quadruplex formation)")
        
        # Homopolymers
        for base in 'ATCG':
            if base*5 in guide:
                warnings.append(f"Contains {base*5} homopolymer")
        
        # Complexity
        unique_bases = len(set(guide))
        if unique_bases < 3:
            warnings.append("Low sequence complexity")
        
        metrics['warnings'] = warnings
        metrics['quality_score'] = max(0, 1 - len(warnings) * 0.15)
        
        return metrics