"""
CRISPR Guide Designer Module
Core functionality for guide RNA design and scoring
"""

import re
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


class CRISPRDesigner:
    """Main class for CRISPR guide RNA design"""
    
    def __init__(self, pam: str = "NGG", spacer_length: int = 20, genome: Optional[str] = None):
        """
        Initialize CRISPR designer
        
        Args:
            pam: PAM sequence (NGG for SpCas9)
            spacer_length: Length of guide spacer (typically 20)
            genome: Reference genome sequence for off-target checking
        """
        self.pam = pam.upper()
        self.spacer_length = spacer_length
        self.genome = genome
        
        # Expanded PAM motifs for SpCas9
        self.pam_motifs = ['GGG', 'AGG', 'CGG', 'TGG']
        
    def find_pam_sites(self, sequence: str) -> List[int]:
        """
        Find all PAM sites in a sequence
        
        Args:
            sequence: DNA sequence to scan
            
        Returns:
            List of PAM positions (start indices)
        """
        sequence = sequence.upper()
        sites = []
        
        for i in range(len(sequence) - 2):
            # Check for NGG pattern
            if sequence[i:i+3] in self.pam_motifs:
                sites.append(i)
                
        return sites
    
    def extract_guides(self, sequence: str) -> List[Dict]:
        """
        Extract guide sequences from a gene sequence
        
        Args:
            sequence: Gene sequence (coding or genomic)
            
        Returns:
            List of guide dictionaries with metadata
        """
        sequence = sequence.upper().replace(' ', '').replace('\n', '')
        guides = []
        pam_sites = self.find_pam_sites(sequence)
        
        for pos in pam_sites:
            start = pos - self.spacer_length
            
            # Skip if not enough upstream sequence
            if start < 0:
                continue
                
            spacer = sequence[start:pos]
            
            # Skip if spacer contains ambiguous bases
            if 'N' in spacer:
                continue
                
            guide = {
                'spacer': spacer,
                'pam': sequence[pos:pos+3],
                'position': start,
                'end': pos + 3,
                'gc_content': self._calc_gc(spacer),
                'poly_t_risk': self._check_poly_t(spacer),
                'poly_g_risk': self._check_poly_g(spacer),
                'homopolymer_risk': self._check_homopolymer(spacer),
                'complexity': self._calc_complexity(spacer),
                'hairpin_risk': self._check_hairpin(spacer)
            }
            
            guides.append(guide)
            
        return guides
    
    def design_guides(self, sequence: str, top_n: int = 50) -> pd.DataFrame:
        """
        Complete guide design workflow returning DataFrame
        
        Args:
            sequence: Gene sequence
            top_n: Number of top guides to return
            
        Returns:
            DataFrame with guide information and scores
        """
        guides = self.extract_guides(sequence)
        
        if not guides:
            return pd.DataFrame()
            
        # Calculate scores
        for guide in guides:
            guide['efficiency_score'] = self.calculate_efficiency_score(guide)
            guide['specificity_score'] = self.calculate_specificity_score(guide)
            guide['combined_score'] = (guide['efficiency_score'] * 0.6 + 
                                      guide['specificity_score'] * 0.4)
        
        # Sort and select top guides
        guides_sorted = sorted(guides, key=lambda x: x['combined_score'], reverse=True)
        
        # Create DataFrame
        df = pd.DataFrame(guides_sorted[:top_n])
        
        # Add ranked position
        df.insert(0, 'rank', range(1, len(df) + 1))
        
        # Format columns for display
        df['gc_percent'] = (df['gc_content'] * 100).round(1)
        df['efficiency_score'] = df['efficiency_score'].round(3)
        df['specificity_score'] = df['specificity_score'].round(3)
        df['combined_score'] = df['combined_score'].round(3)
        
        return df
    
    def calculate_efficiency_score(self, guide: Dict) -> float:
        """
        Calculate guide efficiency based on multiple factors
        
        Based on published guide efficiency rules:
        - GC content (optimal 40-60%)
        - Position of G/C near PAM
        - Poly-T avoidance
        """
        spacer = guide['spacer']
        
        # GC content score (optimal around 50%)
        gc = guide['gc_content']
        gc_score = 1 - abs(gc - 0.5) * 2
        
        # PAM-proximal composition score
        # Guides with G/C in positions 18-20 (near PAM) are more efficient
        pam_proximal = spacer[-3:] if len(spacer) >= 3 else spacer
        pam_score = (pam_proximal.count('G') + pam_proximal.count('C')) / 3
        
        # Poly-T penalty
        poly_t_penalty = 0.7 if guide['poly_t_risk'] else 1.0
        
        # Poly-G penalty
        poly_g_penalty = 0.8 if guide['poly_g_risk'] else 1.0
        
        # Starting base bonus (G start improves expression)
        start_bonus = 1.1 if spacer.startswith('G') else 1.0
        
        # Homopolymer penalty
        homopolymer_penalty = 0.9 if guide['homopolymer_risk'] else 1.0
        
        # Calculate weighted score
        score = (gc_score * 0.4 + pam_score * 0.3) * poly_t_penalty * poly_g_penalty * start_bonus * homopolymer_penalty
        
        return min(1.0, max(0.0, score))
    
    def calculate_specificity_score(self, guide: Dict) -> float:
        """
        Calculate specificity based on guide sequence complexity
        
        Higher complexity = more specific
        """
        spacer = guide['spacer']
        
        # Sequence complexity
        complexity = guide['complexity']
        
        # Number of unique dinucleotides
        dinucleotides = set(spacer[i:i+2] for i in range(len(spacer)-1))
        dinuc_score = len(dinucleotides) / 19
        
        # GC distribution variance
        gc_counts = [spacer[i:i+4].count('G') + spacer[i:i+4].count('C') for i in range(len(spacer)-3)]
        gc_var = np.var(gc_counts) if gc_counts else 0
        gc_var_score = min(1.0, gc_var / 2)
        
        return (complexity * 0.5 + dinuc_score * 0.3 + gc_var_score * 0.2)
    
    def _calc_gc(self, sequence: str) -> float:
        """Calculate GC content"""
        if not sequence:
            return 0
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence)
    
    def _check_poly_t(self, sequence: str) -> bool:
        """Check for poly-T runs (TTTT) that can terminate transcription"""
        return 'TTTT' in sequence
    
    def _check_poly_g(self, sequence: str) -> bool:
        """Check for poly-G runs (GGGG) that can form G-quadruplexes"""
        return 'GGGG' in sequence
    
    def _check_homopolymer(self, sequence: str) -> bool:
        """Check for any homopolymer runs of length 5 or more"""
        return any(c*5 in sequence for c in 'ATCG')
    
    def _calc_complexity(self, sequence: str) -> float:
        """Calculate sequence complexity (proportion of unique k-mers)"""
        if len(sequence) < 8:
            return 1.0
        
        # Count unique 4-mers
        kmers = set(sequence[i:i+4] for i in range(len(sequence)-3))
        complexity = len(kmers) / (len(sequence) - 3)
        
        return min(1.0, complexity * 2)  # Normalize
    
    def _check_hairpin(self, sequence: str) -> bool:
        """
        Check for potential hairpin structures (palindromes)
        Simple check for inverted repeats
        """
        length = len(sequence)
        for i in range(length-6):
            for j in range(i+6, length):
                if sequence[i:j] == sequence[i:j][::-1]:
                    return True
        return False
    
    def get_guide_sequence(self, guide: Dict) -> str:
        """Get full guide sequence including PAM"""
        return guide['spacer'] + guide['pam']
    
    def get_reverse_complement(self, sequence: str) -> str:
        """Get reverse complement of a sequence"""
        return str(Seq(sequence).reverse_complement())


def parse_fasta(file) -> List[SeqRecord]:
    """Parse FASTA file and return list of sequences"""
    sequences = []
    for record in SeqIO.parse(file, "fasta"):
        sequences.append(record)
    return sequences


def validate_sequence(sequence: str) -> Tuple[bool, str]:
    """
    Validate DNA sequence
    
    Returns:
        (is_valid, error_message)
    """
    sequence = sequence.upper().replace(' ', '').replace('\n', '')
    
    if not sequence:
        return False, "Sequence is empty"
    
    if len(sequence) < 20:
        return False, f"Sequence too short (minimum 20 bp, got {len(sequence)})"
    
    valid_bases = set('ATCG')
    invalid_bases = set(sequence) - valid_bases
    
    if invalid_bases:
        return False, f"Invalid bases found: {', '.join(invalid_bases)}"
    
    return True, "Valid sequence"