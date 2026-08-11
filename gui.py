"""
CRISPR Guide Designer - Desktop GUI Application
Built with PyQt5 for a modern, native desktop experience
LARGE FONTS for better readability
"""

import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Import custom modules
from crispr_designer import CRISPRDesigner, validate_sequence, parse_fasta
from off_target import OffTargetAnalyzer, GuideValidator
from utils import (
    validate_fasta, get_sequence_stats, get_download_link,
    format_sequence, generate_example_sequences,
    parse_fasta_string
)
from resources import DARK_STYLE, LIGHT_STYLE

# ============================================================================
# Custom Widgets
# ============================================================================

class LoadingOverlay(QWidget):
    """Loading overlay widget for long operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Spinner label
        self.label = QLabel("Processing...")
        self.label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(0)  # Indeterminate
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4a90e2;
                border-radius: 5px;
                background-color: #16213e;
                min-height: 30px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgba(0,0,0,0.7); border-radius: 10px;")
    
    def showEvent(self, event):
        """Center overlay on parent"""
        if self.parent():
            parent_rect = self.parent().rect()
            self.setGeometry(parent_rect)
        super().showEvent(event)
    
    def set_text(self, text):
        """Update loading text"""
        self.label.setText(text)


class GuideTable(QTableWidget):
    """Custom table widget for guide display with large fonts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #16213e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                gridline-color: #2a2a4a;
                selection-background-color: #4a90e2;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 15px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                padding: 12px 15px;
                border: 1px solid #2a2a4a;
                font-weight: bold;
                color: #8be9fd;
                font-size: 13px;
            }
        """)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(40)


# ============================================================================
# Main Window
# ============================================================================

class CRISPRApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧬 CRISPR Guide Designer - Plant Stress Edition")
        self.setMinimumSize(1200, 800)
        
        # Initialize data FIRST
        self.sequences = {}
        self.guides_df = None
        self.selected_guide = None
        self.off_targets_df = None
        self.current_sequence = ""
        self.current_sequence_name = ""
        
        # Load examples HERE before setting up UI
        self.examples = generate_example_sequences()
        
        # Setup UI
        self.setup_ui()
        self.apply_style()
        self.setup_menu()
        
        # Update stats after UI is ready
        self.update_stats()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Main content area with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                background-color: rgba(26, 26, 46, 0.5);
                padding: 10px;
            }
            QTabBar::tab {
                padding: 14px 28px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
        """)
        
        # Create tabs
        self.input_tab = QWidget()
        self.design_tab = QWidget()
        self.analysis_tab = QWidget()
        self.offtarget_tab = QWidget()
        self.export_tab = QWidget()
        
        self.tab_widget.addTab(self.input_tab, "📝 Input")
        self.tab_widget.addTab(self.design_tab, "🎯 Design Guides")
        self.tab_widget.addTab(self.analysis_tab, "📊 Analysis")
        self.tab_widget.addTab(self.offtarget_tab, "⚠️ Off-Target")
        self.tab_widget.addTab(self.export_tab, "📤 Export")
        
        # Setup each tab
        self.setup_input_tab()
        self.setup_design_tab()
        self.setup_analysis_tab()
        self.setup_offtarget_tab()
        self.setup_export_tab()
        
        main_layout.addWidget(self.tab_widget)
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #1a1a2e;
                color: #888;
                border-top: 1px solid #2a2a4a;
                padding: 5px;
                font-size: 13px;
                min-height: 35px;
            }
        """)
        self.statusBar().showMessage("Ready")
    
    def create_header(self):
        """Create application header with large fonts"""
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title with larger font
        title = QLabel("🧬 CRISPR Guide Designer")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #8be9fd;
        """)
        
        subtitle = QLabel("Plant Stress Tolerance Edition")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #888;
            margin-left: 10px;
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        
        # Quick actions - larger button
        self.run_btn = QPushButton("🚀 Design Guides")
        self.run_btn.clicked.connect(self.design_guides)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #4CAF50, stop: 1 #388E3C);
                font-size: 16px;
                padding: 14px 35px;
                min-height: 45px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #66BB6A, stop: 1 #43A047);
            }
        """)
        header_layout.addWidget(self.run_btn)
        
        header.setLayout(header_layout)
        return header
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border-bottom: 2px solid #2a2a4a;
                padding: 5px;
                font-size: 13px;
            }
            QMenuBar::item:selected {
                background-color: #4a90e2;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QMenu {
                background-color: #1a1a2e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #4a90e2;
                border-radius: 4px;
                padding: 8px 20px;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open FASTA", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_fasta)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Results", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export Report", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        help_action = QAction("&Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_style(self):
        """Apply the dark theme"""
        self.setStyleSheet(DARK_STYLE)
    
    # ========================================================================
    # Input Tab
    # ========================================================================
    
    def setup_input_tab(self):
        """Setup the input tab with large fonts"""
        layout = QVBoxLayout()
        
        # Top row: Sequence input and examples
        top_row = QHBoxLayout()
        
        # Left: Sequence input
        input_group = QGroupBox("Enter Gene Sequence")
        input_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        input_layout = QVBoxLayout()
        
        self.sequence_input = QTextEdit()
        self.sequence_input.setPlaceholderText("Paste your DNA sequence here...\n\nExample:\n>GeneName\nATGGAGGAGCCGCAGTCAGATCCT...")
        self.sequence_input.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 12px;
                color: #e0e0e0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                min-height: 200px;
            }
            QTextEdit:focus {
                border: 2px solid #4a90e2;
            }
        """)
        self.sequence_input.textChanged.connect(self.update_stats)
        input_layout.addWidget(self.sequence_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 Load FASTA File")
        self.load_btn.clicked.connect(self.load_fasta_file)
        self.load_btn.setStyleSheet("font-size: 14px; padding: 12px 20px;")
        btn_layout.addWidget(self.load_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_input)
        self.clear_btn.setStyleSheet("font-size: 14px; padding: 12px 20px;")
        btn_layout.addWidget(self.clear_btn)
        
        input_layout.addLayout(btn_layout)
        input_group.setLayout(input_layout)
        
        # Right: Examples
        example_group = QGroupBox("💡 Example Genes")
        example_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        example_layout = QVBoxLayout()
        
        self.example_combo = QComboBox()
        self.example_combo.addItem("Select an example...")
        for name in self.examples.keys():
            self.example_combo.addItem(name)
        self.example_combo.currentTextChanged.connect(self.load_example)
        self.example_combo.setStyleSheet("font-size: 13px; min-height: 35px;")
        example_layout.addWidget(self.example_combo)
        
        # Example description
        self.example_desc = QLabel("Load a pre-loaded stress response gene sequence to get started.")
        self.example_desc.setStyleSheet("color: #888; font-size: 13px; padding: 10px;")
        self.example_desc.setWordWrap(True)
        example_layout.addWidget(self.example_desc)
        
        example_layout.addStretch()
        example_group.setLayout(example_layout)
        
        top_row.addWidget(input_group, 2)
        top_row.addWidget(example_group, 1)
        layout.addLayout(top_row)
        
        # Bottom: Sequence statistics
        stats_group = QGroupBox("📊 Sequence Statistics")
        stats_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        stats_layout = QHBoxLayout()
        
        self.stats_labels = {}
        stats_metrics = ["Length", "GC%", "A", "T", "G", "C"]
        for metric in stats_metrics:
            label = QLabel(f"{metric}: --")
            label.setStyleSheet("""
                color: #888; 
                font-size: 14px; 
                font-weight: bold; 
                padding: 8px 15px;
                background-color: rgba(26, 26, 46, 0.5);
                border-radius: 6px;
                min-width: 80px;
            """)
            label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(label)
            self.stats_labels[metric] = label
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.input_tab.setLayout(layout)
    
    def load_fasta_file(self):
        """Load a FASTA file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open FASTA File", "",
            "FASTA Files (*.fasta *.fa *.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.sequence_input.setText(content)
                self.statusBar().showMessage(f"Loaded file: {os.path.basename(file_path)}")
                self.update_stats()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def clear_input(self):
        """Clear input"""
        self.sequence_input.clear()
        self.sequences = {}
        self.update_stats()
        self.statusBar().showMessage("Cleared")
    
    def load_example(self, name):
        """Load an example sequence"""
        if name in self.examples:
            self.sequence_input.setText(self.examples[name])
            self.statusBar().showMessage(f"Loaded example: {name}")
            self.update_stats()
    
    def update_stats(self):
        """Update sequence statistics"""
        text = self.sequence_input.toPlainText().strip()
        
        if not text:
            for label in self.stats_labels.values():
                label.setText(label.text().split(':')[0] + ": --")
            return
        
        # Parse sequence
        if text.startswith('>'):
            sequences = validate_fasta(text)
            if sequences:
                seq = sequences[0]['sequence']
            else:
                return
        else:
            seq = ''.join(text.split()).upper()
        
        stats = get_sequence_stats(seq)
        
        self.stats_labels["Length"].setText(f"Length: {stats['length']}")
        self.stats_labels["GC%"].setText(f"GC%: {stats['gc_content']:.1f}%")
        self.stats_labels["A"].setText(f"A: {stats['a_count']}")
        self.stats_labels["T"].setText(f"T: {stats['t_count']}")
        self.stats_labels["G"].setText(f"G: {stats['g_count']}")
        self.stats_labels["C"].setText(f"C: {stats['c_count']}")
    
    # ========================================================================
    # Design Tab
    # ========================================================================
    
    def setup_design_tab(self):
        """Setup the design tab with large fonts"""
        layout = QVBoxLayout()
        
        # Parameters
        param_group = QGroupBox("Design Parameters")
        param_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        param_layout = QHBoxLayout()
        
        # PAM selection
        param_layout.addWidget(QLabel("PAM:"))
        self.pam_combo = QComboBox()
        self.pam_combo.addItems(["NGG", "NAG", "NNGRRT", "NNNNGATT"])
        self.pam_combo.setStyleSheet("font-size: 13px; min-height: 35px;")
        param_layout.addWidget(self.pam_combo)
        
        param_layout.addSpacing(20)
        
        # Guide length
        param_layout.addWidget(QLabel("Guide Length:"))
        self.guide_spin = QSpinBox()
        self.guide_spin.setRange(18, 22)
        self.guide_spin.setValue(20)
        self.guide_spin.setStyleSheet("font-size: 13px; min-height: 35px;")
        param_layout.addWidget(self.guide_spin)
        
        param_layout.addSpacing(20)
        
        # Max mismatches
        param_layout.addWidget(QLabel("Max Mismatches:"))
        self.mismatch_spin = QSpinBox()
        self.mismatch_spin.setRange(1, 6)
        self.mismatch_spin.setValue(4)
        self.mismatch_spin.setStyleSheet("font-size: 13px; min-height: 35px;")
        param_layout.addWidget(self.mismatch_spin)
        
        param_layout.addStretch()
        
        # Design button
        self.design_btn = QPushButton("🔬 Design Guides")
        self.design_btn.clicked.connect(self.design_guides)
        self.design_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #4a90e2, stop: 1 #2c5f8a);
                padding: 12px 30px;
                font-size: 15px;
                min-height: 40px;
                font-weight: bold;
            }
        """)
        param_layout.addWidget(self.design_btn)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Results display
        self.design_results = QWidget()
        results_layout = QVBoxLayout()
        
        # Guide count
        self.guide_count_label = QLabel("No guides designed yet")
        self.guide_count_label.setStyleSheet("color: #888; font-size: 15px; padding: 10px;")
        results_layout.addWidget(self.guide_count_label)
        
        # Guide table
        self.guide_table = GuideTable()
        results_layout.addWidget(self.guide_table)
        
        # Selection details
        detail_group = QGroupBox("Selected Guide Details")
        detail_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        detail_layout = QVBoxLayout()
        
        self.detail_widget = QLabel("Select a guide from the table to view details")
        self.detail_widget.setStyleSheet("color: #888; font-size: 14px; padding: 15px;")
        self.detail_widget.setWordWrap(True)
        detail_layout.addWidget(self.detail_widget)
        
        detail_group.setLayout(detail_layout)
        results_layout.addWidget(detail_group)
        
        self.design_results.setLayout(results_layout)
        layout.addWidget(self.design_results)
        
        self.design_tab.setLayout(layout)
    
    def design_guides(self):
        """Design CRISPR guides"""
        # Get sequence
        text = self.sequence_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter a sequence first")
            return
        
        # Parse sequence
        if text.startswith('>'):
            sequences = validate_fasta(text)
            if sequences:
                seq = sequences[0]['sequence']
                name = sequences[0]['header']
            else:
                QMessageBox.warning(self, "Warning", "Invalid FASTA format")
                return
        else:
            seq = ''.join(text.split()).upper()
            name = "UserSequence"
        
        # Validate
        is_valid, msg = validate_sequence(seq)
        if not is_valid:
            QMessageBox.warning(self, "Warning", f"Invalid sequence: {msg}")
            return
        
        self.current_sequence = seq
        self.current_sequence_name = name
        
        # Show loading overlay
        self.show_loading("Designing guides...")
        
        try:
            # Create designer
            designer = CRISPRDesigner(
                pam=self.pam_combo.currentText(),
                spacer_length=self.guide_spin.value()
            )
            
            # Design guides
            df = designer.design_guides(seq, top_n=50)
            
            self.hide_loading()
            
            if df.empty:
                QMessageBox.information(self, "No Guides", "No potential guides found. Try different parameters.")
                return
            
            self.guides_df = df
            self.display_guides(df)
            
            self.statusBar().showMessage(f"Found {len(df)} potential guides")
            self.tab_widget.setCurrentIndex(1)
            
            # Update analysis tab
            self.update_analysis()
            
        except Exception as e:
            self.hide_loading()
            QMessageBox.critical(self, "Error", f"Failed to design guides: {str(e)}")
    
    def display_guides(self, df):
        """Display guides in table"""
        self.guide_table.setRowCount(0)
        self.guide_table.setColumnCount(8)
        self.guide_table.setHorizontalHeaderLabels([
            "Rank", "Spacer (20bp)", "PAM", "GC%", "Efficiency", 
            "Specificity", "Combined", "Poly-T"
        ])
        
        # Set column widths
        self.guide_table.setColumnWidth(0, 60)
        self.guide_table.setColumnWidth(1, 280)
        self.guide_table.setColumnWidth(2, 70)
        self.guide_table.setColumnWidth(3, 70)
        self.guide_table.setColumnWidth(4, 90)
        self.guide_table.setColumnWidth(5, 90)
        self.guide_table.setColumnWidth(6, 90)
        self.guide_table.setColumnWidth(7, 70)
        
        for i, (_, row) in enumerate(df.iterrows()):
            self.guide_table.insertRow(i)
            self.guide_table.setItem(i, 0, QTableWidgetItem(str(row['rank'])))
            self.guide_table.setItem(i, 1, QTableWidgetItem(row['spacer']))
            self.guide_table.setItem(i, 2, QTableWidgetItem(row['pam']))
            self.guide_table.setItem(i, 3, QTableWidgetItem(f"{row['gc_percent']:.1f}%"))
            self.guide_table.setItem(i, 4, QTableWidgetItem(f"{row['efficiency_score']:.3f}"))
            self.guide_table.setItem(i, 5, QTableWidgetItem(f"{row['specificity_score']:.3f}"))
            self.guide_table.setItem(i, 6, QTableWidgetItem(f"{row['combined_score']:.3f}"))
            self.guide_table.setItem(i, 7, QTableWidgetItem("⚠️" if row['poly_t_risk'] else "✓"))
            
            # Color coding
            for col in range(4, 7):
                item = self.guide_table.item(i, col)
                val = float(item.text())
                if val >= 0.8:
                    item.setBackground(QColor(46, 125, 50, 100))  # Green
                elif val >= 0.6:
                    item.setBackground(QColor(237, 108, 2, 100))   # Orange
                else:
                    item.setBackground(QColor(183, 28, 28, 100))   # Red
        
        # Connect selection
        self.guide_table.itemSelectionChanged.connect(self.on_guide_selected)
        
        self.guide_count_label.setText(f"Found {len(df)} potential guides")
    
    def on_guide_selected(self):
        """Handle guide selection"""
        selected_rows = self.guide_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row < 0 or self.guides_df is None:
            return
        
        guide = self.guides_df.iloc[row]
        self.selected_guide = guide.to_dict()
        
        # Update details
        detail_text = f"""
        <b>Guide #{guide['rank']}</b><br><br>
        <b>Sequence:</b> <span style="font-family: monospace; font-size: 15px;">
        5′-{guide['spacer']}<span style="color: #ff6b6b; font-weight: bold;">{guide['pam']}</span>-3′</span><br><br>
        <b>Position:</b> {guide['position']}<br>
        <b>GC Content:</b> {guide['gc_percent']:.1f}%<br>
        <b>Efficiency Score:</b> {guide['efficiency_score']:.3f}<br>
        <b>Specificity Score:</b> {guide['specificity_score']:.3f}<br>
        <b>Combined Score:</b> <span style="color: #8be9fd; font-weight: bold; font-size: 16px;">{guide['combined_score']:.3f}</span><br>
        """
        
        if guide.get('poly_t_risk', False):
            detail_text += '<br><span style="color: #ff6b6b; font-size: 14px;">⚠️ Contains poly-T run (TTTT)</span>'
        if guide.get('poly_g_risk', False):
            detail_text += '<br><span style="color: #ff6b6b; font-size: 14px;">⚠️ Contains poly-G run (GGGG)</span>'
        
        self.detail_widget.setText(detail_text)
        
        # Enable off-target button
        self.offtarget_btn.setEnabled(True)
    
    # ========================================================================
    # Analysis Tab
    # ========================================================================
    
    def setup_analysis_tab(self):
        """Setup analysis tab with large fonts"""
        layout = QVBoxLayout()
        
        # Stats cards
        self.stats_card = QWidget()
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_label = QLabel("Total: --")
        self.total_label.setStyleSheet("color: #8be9fd; font-size: 20px; font-weight: bold; padding: 10px;")
        stats_layout.addWidget(self.total_label)
        
        self.best_label = QLabel("Best: --")
        self.best_label.setStyleSheet("color: #4CAF50; font-size: 20px; font-weight: bold; padding: 10px;")
        stats_layout.addWidget(self.best_label)
        
        self.avg_gc_label = QLabel("Avg GC%: --")
        self.avg_gc_label.setStyleSheet("color: #FFD700; font-size: 20px; font-weight: bold; padding: 10px;")
        stats_layout.addWidget(self.avg_gc_label)
        
        self.risky_label = QLabel("Risky: --")
        self.risky_label.setStyleSheet("color: #ff6b6b; font-size: 20px; font-weight: bold; padding: 10px;")
        stats_layout.addWidget(self.risky_label)
        
        stats_layout.addStretch()
        self.stats_card.setLayout(stats_layout)
        layout.addWidget(self.stats_card)
        
        # Charts area
        charts_group = QGroupBox("Visualizations")
        charts_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        charts_layout = QHBoxLayout()
        
        # GC distribution
        self.gc_figure = Figure(figsize=(5, 4), facecolor='#1a1a2e')
        self.gc_ax = self.gc_figure.add_subplot(111)
        self.gc_ax.set_facecolor('#16213e')
        self.gc_ax.tick_params(colors='#888', labelsize=11)
        self.gc_ax.set_xlabel('GC%', color='#888', fontsize=12)
        self.gc_ax.set_ylabel('Count', color='#888', fontsize=12)
        self.gc_ax.set_title('GC Distribution', color='#8be9fd', fontsize=13)
        self.gc_canvas = FigureCanvas(self.gc_figure)
        charts_layout.addWidget(self.gc_canvas)
        
        # Score scatter
        self.score_figure = Figure(figsize=(5, 4), facecolor='#1a1a2e')
        self.score_ax = self.score_figure.add_subplot(111)
        self.score_ax.set_facecolor('#16213e')
        self.score_ax.tick_params(colors='#888', labelsize=11)
        self.score_ax.set_xlabel('Efficiency', color='#888', fontsize=12)
        self.score_ax.set_ylabel('Specificity', color='#888', fontsize=12)
        self.score_ax.set_title('Efficiency vs Specificity', color='#8be9fd', fontsize=13)
        self.score_canvas = FigureCanvas(self.score_figure)
        charts_layout.addWidget(self.score_canvas)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
        
        self.analysis_tab.setLayout(layout)
    
    def update_analysis(self):
        """Update analysis tab with current data"""
        if self.guides_df is None or self.guides_df.empty:
            return
        
        df = self.guides_df
        
        # Update stats
        self.total_label.setText(f"Total: {len(df)}")
        self.best_label.setText(f"Best: {df['combined_score'].max():.3f}")
        self.avg_gc_label.setText(f"Avg GC%: {df['gc_percent'].mean():.1f}%")
        self.risky_label.setText(f"Risky: {df['poly_t_risk'].sum()}")
        
        # Update charts
        self.gc_ax.clear()
        self.gc_ax.hist(df['gc_percent'], bins=15, color='#4a90e2', alpha=0.7, edgecolor='white')
        self.gc_ax.set_facecolor('#16213e')
        self.gc_ax.tick_params(colors='#888', labelsize=11)
        self.gc_ax.set_xlabel('GC%', color='#888', fontsize=12)
        self.gc_ax.set_ylabel('Count', color='#888', fontsize=12)
        self.gc_ax.set_title('GC Distribution', color='#8be9fd', fontsize=13)
        self.gc_canvas.draw()
        
        self.score_ax.clear()
        self.score_ax.scatter(df['efficiency_score'], df['specificity_score'], 
                            c=df['gc_percent'], cmap='RdYlGn', alpha=0.7, s=60)
        self.score_ax.set_facecolor('#16213e')
        self.score_ax.tick_params(colors='#888', labelsize=11)
        self.score_ax.set_xlabel('Efficiency', color='#888', fontsize=12)
        self.score_ax.set_ylabel('Specificity', color='#888', fontsize=12)
        self.score_ax.set_title('Efficiency vs Specificity', color='#8be9fd', fontsize=13)
        self.score_canvas.draw()
    
    # ========================================================================
    # Off-Target Tab
    # ========================================================================
    
    def setup_offtarget_tab(self):
        """Setup off-target analysis tab with large fonts"""
        layout = QVBoxLayout()
        
        # Input
        input_group = QGroupBox("Off-Target Analysis")
        input_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        input_layout = QVBoxLayout()
        
        self.offtarget_genome = QTextEdit()
        self.offtarget_genome.setPlaceholderText("Paste your reference genome sequence for off-target search...")
        self.offtarget_genome.setMaximumHeight(120)
        self.offtarget_genome.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 12px;
                color: #e0e0e0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #4a90e2;
            }
        """)
        input_layout.addWidget(self.offtarget_genome)
        
        btn_layout = QHBoxLayout()
        
        self.offtarget_btn = QPushButton("🔍 Find Off-Targets")
        self.offtarget_btn.clicked.connect(self.find_offtargets)
        self.offtarget_btn.setEnabled(False)
        self.offtarget_btn.setStyleSheet("""
            font-size: 15px; 
            padding: 12px 30px; 
            min-height: 40px;
            font-weight: bold;
        """)
        btn_layout.addWidget(self.offtarget_btn)
        
        input_layout.addLayout(btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Results
        self.offtarget_results = QLabel("Select a guide in the Design tab and run off-target analysis")
        self.offtarget_results.setStyleSheet("color: #888; font-size: 14px; padding: 30px;")
        self.offtarget_results.setAlignment(Qt.AlignCenter)
        self.offtarget_results.setWordWrap(True)
        layout.addWidget(self.offtarget_results)
        
        self.offtarget_tab.setLayout(layout)
    
    def find_offtargets(self):
        """Find off-target sites"""
        if self.selected_guide is None:
            QMessageBox.warning(self, "Warning", "Please select a guide first")
            return
        
        genome = self.offtarget_genome.toPlainText().strip()
        if not genome:
            QMessageBox.warning(self, "Warning", "Please paste a genome sequence")
            return
        
        self.show_loading("Analyzing off-target effects...")
        
        try:
            guide_seq = self.selected_guide['spacer']
            genome = ''.join(genome.split()).upper()
            
            analyzer = OffTargetAnalyzer(
                genome=genome,
                max_mismatches=self.mismatch_spin.value()
            )
            
            df = analyzer.analyze_guide(guide_seq, genome, self.mismatch_spin.value())
            
            self.hide_loading()
            
            if df.empty:
                self.offtarget_results.setText("✅ No significant off-target sites found!")
                self.offtarget_results.setStyleSheet("color: #4CAF50; font-size: 18px; padding: 30px; font-weight: bold;")
            else:
                self.off_targets_df = df
                
                text = f"⚠️ Found {len(df)} potential off-target sites\n\n"
                text += "Top 10 off-target sites:\n"
                text += df[['position', 'mismatches', 'severity']].head(10).to_string(index=False)
                
                self.offtarget_results.setText(text)
                self.offtarget_results.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 20px; font-family: monospace;")
                
        except Exception as e:
            self.hide_loading()
            QMessageBox.critical(self, "Error", f"Off-target analysis failed: {str(e)}")
    
    # ========================================================================
    # Export Tab
    # ========================================================================
    
    def setup_export_tab(self):
        """Setup export tab with large fonts"""
        layout = QVBoxLayout()
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        export_layout = QVBoxLayout()
        
        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Format:"))
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "Excel", "JSON"])
        self.export_format.setStyleSheet("font-size: 13px; min-height: 35px;")
        format_row.addWidget(self.export_format)
        format_row.addStretch()
        export_layout.addLayout(format_row)
        
        btn_row = QHBoxLayout()
        
        self.export_guides_btn = QPushButton("📥 Download Guides")
        self.export_guides_btn.clicked.connect(self.export_guides)
        self.export_guides_btn.setStyleSheet("font-size: 14px; padding: 12px 25px; min-height: 40px;")
        btn_row.addWidget(self.export_guides_btn)
        
        self.export_offtarget_btn = QPushButton("📥 Download Off-Targets")
        self.export_offtarget_btn.clicked.connect(self.export_offtargets)
        self.export_offtarget_btn.setStyleSheet("font-size: 14px; padding: 12px 25px; min-height: 40px;")
        btn_row.addWidget(self.export_offtarget_btn)
        
        export_layout.addLayout(btn_row)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Report generation
        report_group = QGroupBox("Generate Report")
        report_group.setStyleSheet("QGroupBox { font-size: 15px; }")
        report_layout = QVBoxLayout()
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMaximumHeight(200)
        self.report_text.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                border: 2px solid #2a2a4a;
                border-radius: 8px;
                padding: 12px;
                color: #e0e0e0;
                font-size: 13px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        report_layout.addWidget(self.report_text)
        
        self.generate_report_btn = QPushButton("📊 Generate Report")
        self.generate_report_btn.clicked.connect(self.generate_report)
        self.generate_report_btn.setStyleSheet("font-size: 14px; padding: 12px 25px; min-height: 40px;")
        report_layout.addWidget(self.generate_report_btn)
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        layout.addStretch()
        
        self.export_tab.setLayout(layout)
    
    def export_guides(self):
        """Export guides to file"""
        if self.guides_df is None or self.guides_df.empty:
            QMessageBox.warning(self, "Warning", "No guides to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Guides", "crispr_guides",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            fmt = self.export_format.currentText()
            df = self.guides_df
            
            if fmt == "CSV" or file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif fmt == "Excel" or file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False, engine='openpyxl')
            else:
                df.to_json(file_path, orient='records')
            
            self.statusBar().showMessage(f"Exported guides to {file_path}")
            QMessageBox.information(self, "Success", f"Guides exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def export_offtargets(self):
        """Export off-target results"""
        if self.off_targets_df is None or self.off_targets_df.empty:
            QMessageBox.warning(self, "Warning", "No off-target data to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Off-Targets", "offtargets.csv",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.off_targets_df.to_csv(file_path, index=False)
            self.statusBar().showMessage(f"Exported off-targets to {file_path}")
            QMessageBox.information(self, "Success", f"Off-targets exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def generate_report(self):
        """Generate summary report"""
        if self.guides_df is None or self.guides_df.empty:
            QMessageBox.warning(self, "Warning", "No guides to report")
            return
        
        df = self.guides_df
        
        report = f"""
CRISPR Guide Design Report
==========================

Sequence: {self.current_sequence_name}
Date: {QDate.currentDate().toString()}

Summary Statistics:
-------------------
- Total guides designed: {len(df)}
- Average GC content: {df['gc_percent'].mean():.1f}%
- Best combined score: {df['combined_score'].max():.3f}
- Guides with poly-T risk: {df['poly_t_risk'].sum()}

Top 5 Guides:
-------------
"""
        for _, row in df.head(5).iterrows():
            report += f"#{row['rank']}: {row['spacer']} "
            report += f"(GC: {row['gc_percent']:.1f}%, Score: {row['combined_score']:.3f})\n"
        
        risky = df[df['poly_t_risk']]
        if not risky.empty:
            report += f"\nRisky Guides (poly-T):\n"
            for _, row in risky.iterrows():
                report += f"#{row['rank']}: {row['spacer']}\n"
        else:
            report += "\nNo poly-T risks detected.\n"
        
        # Off-target summary
        if self.off_targets_df is not None and not self.off_targets_df.empty:
            report += f"\nOff-Target Summary:\n"
            report += f"- Total off-targets found: {len(self.off_targets_df)}\n"
            report += f"- High risk: {len(self.off_targets_df[self.off_targets_df['severity'] == 'High risk'])}\n"
            report += f"- Medium risk: {len(self.off_targets_df[self.off_targets_df['severity'] == 'Medium risk'])}\n"
        
        self.report_text.setText(report)
        
        # Save to file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "crispr_report.txt",
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(report)
                self.statusBar().showMessage(f"Report saved to {file_path}")
                QMessageBox.information(self, "Success", f"Report saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def show_loading(self, text="Processing..."):
        """Show loading overlay"""
        if not hasattr(self, 'loading_overlay'):
            self.loading_overlay = LoadingOverlay(self.centralWidget())
        self.loading_overlay.set_text(text)
        self.loading_overlay.show()
        QApplication.processEvents()
    
    def hide_loading(self):
        """Hide loading overlay"""
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.hide()
    
    def save_results(self):
        """Save current results"""
        if self.guides_df is None or self.guides_df.empty:
            QMessageBox.warning(self, "Warning", "No results to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "crispr_results.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.guides_df.to_csv(file_path, index=False)
                self.statusBar().showMessage(f"Results saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def open_fasta(self):
        """Open FASTA file"""
        self.load_fasta_file()
    
    def export_report(self):
        """Export report"""
        self.tab_widget.setCurrentIndex(4)  # Export tab
        self.generate_report()
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        <h2 style="font-size: 22px;">🧬 CRISPR Guide Designer Help</h2>
        
        <h3 style="font-size: 16px;">1. Input Sequence</h3>
        <p style="font-size: 14px;">Paste your gene sequence in FASTA format or as plain DNA sequence.</p>
        
        <h3 style="font-size: 16px;">2. Design Guides</h3>
        <p style="font-size: 14px;">Click "Design Guides" to find potential CRISPR guides. The tool will scan for PAM sites and score each guide.</p>
        
        <h3 style="font-size: 16px;">3. Analyze Results</h3>
        <p style="font-size: 14px;">View guide statistics, GC distribution, and efficiency vs specificity plots.</p>
        
        <h3 style="font-size: 16px;">4. Off-Target Analysis</h3>
        <p style="font-size: 14px;">Paste a reference genome and analyze potential off-target effects for a selected guide.</p>
        
        <h3 style="font-size: 16px;">5. Export</h3>
        <p style="font-size: 14px;">Export guides and off-target data in CSV, Excel, or JSON format.</p>
        
        <h3 style="font-size: 16px;">Keyboard Shortcuts</h3>
        <p style="font-size: 14px;">Ctrl+O: Open FASTA file<br>
        Ctrl+S: Save results<br>
        Ctrl+E: Export report<br>
        Ctrl+Q: Exit</p>
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2 style="font-size: 22px;">🧬 CRISPR Guide Designer</h2>
        <p style="font-size: 14px;"><b>Version:</b> 2.0</p>
        <p style="font-size: 14px;"><b>Plant Stress Edition</b></p>
        <br>
        <p style="font-size: 14px;">A comprehensive tool for designing CRISPR guides<br>
        for plant stress tolerance genes.</p>
        <br>
        <p style="font-size: 14px;">Built with PyQt5, Biopython, and Matplotlib</p>
        <br>
        <p style="font-size: 14px;">© 2024 Plant Stress Research</p>
        """
        
        QMessageBox.about(self, "About CRISPR Guide Designer", about_text)


# ============================================================================
# Application Entry Point
# ============================================================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application icon
    app.setWindowIcon(QIcon())
    
    # Create and show main window
    window = CRISPRApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()