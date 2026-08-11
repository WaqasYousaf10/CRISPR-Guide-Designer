# 🧬 CRISPR Guide Designer - Plant Stress Edition

A desktop application for designing CRISPR guide RNAs for plant stress tolerance genes.

## 📥 Download

### ⚡ Quick Download (Recommended)

[![Download EXE](https://img.shields.io/badge/Download-EXE-4CAF50?style=for-the-badge&logo=google-drive&logoColor=white)](https://drive.google.com/file/d/1MvZPclshJDeRLf7yq4Mqtho3Yg_gMbXi/view?usp=sharing)

**Click the button above** to download `CRISPR_Guide_Designer.exe`

> 💡 **No Python installation needed!** Just download and double-click to run.

**Alternative Downloads:**
- 📦 [ZIP Archive (GitHub Releases)](https://github.com/YOUR-USERNAME/CRISPR-Guide-Designer/releases)
- 📖 [View Source Code](https://github.com/YOUR-USERNAME/CRISPR-Guide-Designer)

---

## 🎯 Features

- **Guide Design**: Find optimal CRISPR guides for any gene sequence
- **Intelligent Scoring**: Multi-factor scoring (GC content, specificity, efficiency)
- **Off-Target Analysis**: Predict potential off-target effects
- **Visualizations**: Interactive plots for guide quality analysis
- **Export Results**: CSV, Excel, or JSON formats
- **Plant Stress Focus**: Pre-loaded example genes (SOS1, DREB1A, NAC)
- **Beautiful Dark Theme**: Large, readable fonts

## 📖 How It Works

This app helps you design CRISPR guide RNAs. The logic is simple:

1. **Input your gene sequence** (paste DNA or load FASTA file)
2. **Scan for PAM sites** - the app looks for NGG sequences where Cas9 binds
3. **Extract guides** - takes 20 bases before each PAM site
4. **Score each guide** based on:
   - GC Content (optimal 40-60%)
   - No poly-T runs (TTTT stops transcription)
   - Sequence specificity (less off-target cutting)
5. **Rank results** - best guides have combined scores > 0.7

## 📚 How to Use

1. **Open the app** - Double-click the EXE
2. **Load a sequence** - Use an example gene or paste your own
3. **Click "Design Guides"** - The app finds and scores all guides
4. **Select a guide** - Choose the one with the highest combined score
5. **Export results** - Save as CSV for ordering guides

## 🛠️ Technologies

- **Python 3.8+**
- **PyQt5** - GUI framework
- **Biopython** - DNA sequence processing
- **Pandas/NumPy** - Data analysis
- **Matplotlib** - Visualizations

## 📝 License

MIT License

---

**Happy CRISPR editing! 🧬**
