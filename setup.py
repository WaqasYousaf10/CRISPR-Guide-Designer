"""
Setup script for CRISPR Guide Designer
"""

from setuptools import setup, find_packages

setup(
    name="crispr-guide-designer",
    version="2.0.0",
    description="CRISPR Guide Designer for Plant Stress Research",
    author="Plant Stress Research",
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.9',
        'biopython>=1.81',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'requests>=2.31.0',
        'openpyxl>=3.1.0',
    ],
    entry_points={
        'console_scripts': [
            'crispr-designer=gui:main',
        ],
    },
    python_requires='>=3.8',
)