"""
Utility functions for the CRISPR app
"""

import re
import base64
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from Bio import SeqIO, Entrez
from io import StringIO


def validate_fasta(file_content: str) -> List[Dict]:
    """
    Validate and parse FASTA content
    
    Returns:
        List of sequences with metadata
    """
    sequences = []
    current_header = None
    current_seq = []
    
    for line in file_content.split('\n'):
        line = line.strip()
        
        if line.startswith('>'):
            if current_header:
                sequences.append({
                    'header': current_header,
                    'sequence': ''.join(current_seq).upper()
                })
            current_header = line[1:]  # Remove '>'
            current_seq = []
        elif line:
            current_seq.append(line)
    
    if current_header:
        sequences.append({
            'header': current_header,
            'sequence': ''.join(current_seq).upper()
        })
    
    return sequences


def get_gene_info(gene_id: str) -> Dict:
    """
    Fetch gene information from NCBI
    """
    try:
        Entrez.email = "user@example.com"
        
        handle = Entrez.esummary(db="gene", id=gene_id)
        record = Entrez.read(handle)
        
        if record:
            gene_info = {
                'id': gene_id,
                'name': record[0].get('Name', 'Unknown'),
                'description': record[0].get('Description', 'No description'),
                'taxonomy': record[0].get('TaxId', 'Unknown')
            }
            return gene_info
        
    except Exception as e:
        print(f"Error fetching gene info: {e}")
    
    return {}


def format_sequence(sequence: str, line_width: int = 60) -> str:
    """Format sequence with line breaks for display"""
    return '\n'.join(sequence[i:i+line_width] 
                     for i in range(0, len(sequence), line_width))


def get_download_link(df: pd.DataFrame, filename: str = "guides.csv") -> str:
    """Generate download link for DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href


def get_sequence_stats(sequence: str) -> Dict:
    """Calculate basic sequence statistics"""
    sequence = sequence.upper()
    
    stats = {
        'length': len(sequence),
        'gc_content': (sequence.count('G') + sequence.count('C')) / len(sequence) * 100,
        'a_count': sequence.count('A'),
        't_count': sequence.count('T'),
        'g_count': sequence.count('G'),
        'c_count': sequence.count('C'),
    }
    
    return stats


def color_guide(guide: str, mismatches: List[int] = None) -> str:
    """
    Color code guide sequence for display
    
    Args:
        guide: Guide sequence
        mismatches: Positions of mismatches (for off-target display)
    """
    colors = {
        'A': '#FF6B6B',  # Red
        'T': '#4ECDC4',  # Teal
        'G': '#45B7D1',  # Blue
        'C': '#96CEB4',  # Green
    }
    
    if mismatches:
        # Highlight mismatches differently
        highlighted = []
        for i, base in enumerate(guide):
            if i in mismatches:
                highlighted.append(f'<span style="background-color:#FFD93D;font-weight:bold">{base}</span>')
            else:
                highlighted.append(f'<span style="color:{colors.get(base, "#333")}">{base}</span>')
        return ''.join(highlighted)
    else:
        # Simple colored display
        return ''.join(f'<span style="color:{colors.get(base, "#333")};font-weight:bold">{base}</span>' 
                      for base in guide)


def parse_fasta_string(fasta_string: str) -> Dict[str, str]:
    """Parse FASTA string into dictionary of sequences"""
    sequences = {}
    current_id = None
    current_seq = []
    
    for line in fasta_string.strip().split('\n'):
        line = line.strip()
        if line.startswith('>'):
            if current_id:
                sequences[current_id] = ''.join(current_seq)
            current_id = line[1:].split()[0]  # Take first part as ID
            current_seq = []
        elif line and current_id:
            current_seq.append(line)
    
    if current_id:
        sequences[current_id] = ''.join(current_seq)
    
    return sequences


def generate_example_sequences() -> Dict[str, str]:
    """Generate example stress-related gene sequences"""
    examples = {
        'AtSOS1 (Salt Tolerance)': """
>AtSOS1 Salt Overly Sensitive 1
ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAA
ACTGTGAGTGGATCCATTGGAAGGGCCAAAGAAGCCGATCTGACCGAGACTTGGAAACTTGCTCGGAGAG
CCAAGGCAGCTGTTCCTAAGCGAAAGAAAGGAGCACCTTCTTCAGCCGACGATGACGAATCGTCGGTTTC
GGGTTCGGCGGTGGTGAGGAGGAAGAATGACAAGGTGAGATTGTCCGGTGAACGTTGGGTTGCCGTGGTT
GTTGGCGCCGGTGTTGGTGGTGGTTGTTGTTGTGGTGGTGCAGTGGCTGGTGCTGGTGCTGCTTCGAGA
TGCTGCATTATGTGGTCAGCATCCGTTGTTGTGGCGCCGATTTGGTGAGCGGAGAAATCGGAGGGAGTG
""",
        'OsDREB1A (Drought Tolerance)': """
>OsDREB1A Dehydration Responsive Element Binding Protein 1A
ATGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGTGGAAGCAGCTCAGCTCCA
GGAGATCACCACCACCAACGCCGCCGCCGCCGCCGCCTACGAAGCCGCCGCCGCCTTCGCCTCCTCCTC
CTCCACCGACATCACCATCAACGGCGGCAACGGCGGCGCCGACGGCGGCGGCGGCGGCGGCGGCGGCAG
CGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCTACCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
""",
        'ZmNAC (Drought Tolerance)': """
>ZmNAC Maize NAC Transcription Factor
ATGGAGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC
"""
    }
    return examples