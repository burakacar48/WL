import sys
import itertools
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QTextEdit, QScrollArea, QTabWidget, QGridLayout, 
                           QFrame, QStatusBar, QTableWidget, QTableWidgetItem, QComboBox,
                           QCheckBox, QSpinBox, QFileDialog, QProgressBar, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette

class ModernBaccaratAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.results = []
        self.pattern_stats = {}
        self.matrix_stats = {}
        self.adaptive_stats = {}
        self.prediction_stats = {
            'total_predictions': 0,
            'correct': 0,
            'incorrect': 0,
            'current_win_streak': 0,
            'max_win_streak': 0,
            'current_loss_streak': 0,
            'max_loss_streak': 0
        }
        self.prediction_history = []  
        self.loss_streak_predictions = []  
        self.significance_threshold = 5  
        self.active_algorithm = "pattern"  
        self.initUI()
        
    def initUI(self):
        # Set main window properties
        self.setWindowTitle('WL Pattern Analyzer')
        self.setFixedSize(550, 420)
        
        # Apply dark theme styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                color: #e6e6e6;
                font-size: 9pt;
            }
            QLabel {
                color: #a0a7c6;
            }
            QLabel#header {
                color: #e6e6e6;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #444863;
                border: none;
                border-radius: 3px;
                padding: 4px;
                color: #c5cee0;
            }
            QPushButton:hover {
                background-color: #505580;
            }
            QPushButton#win {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
            }
            QPushButton#loss {
                background-color: #c62828;
                color: white;
                font-weight: bold;
            }
            QPushButton#add {
                background-color: #1565c0;
                color: white;
                font-weight: bold;
            }
            QComboBox, QSpinBox {
                background-color: #16182c;
                border: 1px solid #2d3154;
                border-radius: 3px;
                padding: 2px;
                color: #c5cee0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 8px;
                height: 8px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #1d203a;
                width: 16px;
            }
            QTextEdit {
                background-color: #16182c;
                border: 1px solid #2d3154;
                border-radius: 3px;
                color: #c5cee0;
            }
            QTabWidget::pane {
                background-color: #1d203a;
                border: none;
                border-radius: 4px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #1d203a;
                color: #a0a7c6;
                padding: 5px 10px;
                margin-right: 2px;
                min-width: 50px;
                font-size: 9pt;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #16182c;
                color: white;
            }
            QFrame#panel {
                background-color: #222442;
                border-radius: 4px;
            }
            QFrame#content {
                background-color: #16182c;
                border: 1px solid #2d3154;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #2d3154;
                border-radius: 6px;
                background-color: #1d203a;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4364c8;
                border-radius: 6px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create left panel (controls)
        left_panel = QFrame()
        left_panel.setObjectName("panel")
        left_panel.setFixedWidth(160)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)
        
        # Algorithm selection
        algo_label = QLabel("Algorithm")
        left_layout.addWidget(algo_label)
        
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["Pattern Analysis", "Matrix Analysis", "Adaptive Analysis", "Combined Analysis"])
        self.algo_combo.currentIndexChanged.connect(self.change_algorithm)
        left_layout.addWidget(self.algo_combo)
        
        # Sample size control
        sample_label = QLabel("Min. Sample Size")
        left_layout.addWidget(sample_label)
        
        self.sample_spin = QSpinBox()
        self.sample_spin.setRange(1, 100)
        self.sample_spin.setValue(5)
        self.sample_spin.valueChanged.connect(self.update_significance_threshold)
        left_layout.addWidget(self.sample_spin)
        
        # Pattern length control
        pattern_label = QLabel("Pattern Length")
        left_layout.addWidget(pattern_label)
        
        self.pattern_spin = QSpinBox()
        self.pattern_spin.setRange(3, 7)
        self.pattern_spin.setValue(5)
        left_layout.addWidget(self.pattern_spin)
        
        # Win/Loss buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.win_button = QPushButton('WIN (W)')
        self.win_button.setObjectName("win")
        self.win_button.setFixedHeight(32)
        self.win_button.clicked.connect(lambda: self.add_result('W'))
        
        self.loss_button = QPushButton('LOSS (L)')
        self.loss_button.setObjectName("loss")
        self.loss_button.setFixedHeight(32)
        self.loss_button.clicked.connect(lambda: self.add_result('L'))
        
        buttons_layout.addWidget(self.win_button)
        buttons_layout.addWidget(self.loss_button)
        
        left_layout.addLayout(buttons_layout)
        
        # Bulk input
        bulk_label = QLabel("Bulk Entry")
        left_layout.addWidget(bulk_label)
        
        self.bulk_input = QTextEdit()
        self.bulk_input.setMaximumHeight(38)
        self.bulk_input.setPlaceholderText("Enter W L W W L L...")
        left_layout.addWidget(self.bulk_input)
        
        bulk_button = QPushButton('ADD BULK RESULTS')
        bulk_button.setObjectName("add")
        bulk_button.setFixedHeight(24)
        bulk_button.clicked.connect(self.add_bulk_results)
        left_layout.addWidget(bulk_button)
        
        # Control buttons
        control_layout1 = QHBoxLayout()
        control_layout1.setSpacing(8)
        
        delete_button = QPushButton('DELETE')
        delete_button.setFixedHeight(24)
        delete_button.clicked.connect(self.delete_last_result)
        
        clear_button = QPushButton('CLEAR')
        clear_button.setFixedHeight(24)
        clear_button.clicked.connect(self.clear_all_results)
        
        control_layout1.addWidget(delete_button)
        control_layout1.addWidget(clear_button)
        
        left_layout.addLayout(control_layout1)
        
        # File operations
        file_layout = QHBoxLayout()
        file_layout.setSpacing(8)
        
        load_button = QPushButton('LOAD')
        load_button.setFixedHeight(24)
        load_button.clicked.connect(self.load_results)
        
        save_button = QPushButton('SAVE')
        save_button.setFixedHeight(24)
        save_button.clicked.connect(self.save_results)
        
        file_layout.addWidget(load_button)
        file_layout.addWidget(save_button)
        
        left_layout.addLayout(file_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)
        
        # Add left panel to main layout
        main_layout.addWidget(left_panel)
        
        # Create right panel (content area)
        right_panel = QFrame()
        right_panel.setObjectName("panel")
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Tab 1: Prediction
        prediction_tab = QWidget()
        prediction_layout = QVBoxLayout(prediction_tab)
        prediction_layout.setContentsMargins(8, 8, 8, 8)
        prediction_layout.setSpacing(8)
        
        # Current prediction box
        prediction_frame = QFrame()
        prediction_frame.setObjectName("content")
        prediction_layout_inner = QVBoxLayout(prediction_frame)
        
        prediction_header = QLabel("CURRENT PREDICTION")
        prediction_header.setObjectName("header")
        prediction_layout_inner.addWidget(prediction_header)
        
        prediction_grid = QGridLayout()
        prediction_grid.setVerticalSpacing(6)
        prediction_grid.setHorizontalSpacing(10)
        
        # Algorithm label and value
        algo_label_pred = QLabel("Algorithm:")
        algo_value_pred = QLabel("Pattern Analysis")
        algo_value_pred.setStyleSheet("color: #c5cee0;")
        prediction_grid.addWidget(algo_label_pred, 0, 0)
        prediction_grid.addWidget(algo_value_pred, 0, 1)
        
        # Pattern label and value
        pattern_label_pred = QLabel("Pattern:")
        self.pattern_value_pred = QLabel("-")
        self.pattern_value_pred.setStyleSheet("color: #c5cee0;")
        prediction_grid.addWidget(pattern_label_pred, 1, 0)
        prediction_grid.addWidget(self.pattern_value_pred, 1, 1)
        
        # Success rate label and value
        success_label_pred = QLabel("Success Rate:")
        self.success_value_pred = QLabel("-")
        self.success_value_pred.setStyleSheet("color: #c5cee0;")
        prediction_grid.addWidget(success_label_pred, 2, 0)
        prediction_grid.addWidget(self.success_value_pred, 2, 1)
        
        # Recommendation label and value
        recommend_label_pred = QLabel("Recommendation:")
        self.recommend_value_pred = QLabel("-")
        self.recommend_value_pred.setStyleSheet("color: #c5cee0; font-size: 12pt; font-weight: bold;")
        prediction_grid.addWidget(recommend_label_pred, 3, 0)
        prediction_grid.addWidget(self.recommend_value_pred, 3, 1)
        
        prediction_layout_inner.addLayout(prediction_grid)
        prediction_layout.addWidget(prediction_frame)
        
        # Recent results box
        recent_frame = QFrame()
        recent_frame.setObjectName("content")
        recent_layout = QVBoxLayout(recent_frame)
        
        recent_header = QLabel("RECENT RESULTS")
        recent_header.setObjectName("header")
        recent_layout.addWidget(recent_header)
        
        self.recent_grid = QGridLayout()
        self.recent_grid.setSpacing(5)
        recent_layout.addLayout(self.recent_grid)
        
        prediction_layout.addWidget(recent_frame)
        
        # Stats box
        stats_frame = QFrame()
        stats_frame.setObjectName("content")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_header = QLabel("STATISTICS")
        stats_header.setObjectName("header")
        stats_layout.addWidget(stats_header)
        
        stats_grid = QGridLayout()
        stats_grid.setVerticalSpacing(6)
        stats_grid.setHorizontalSpacing(10)
        
        # Left column stats
        total_label = QLabel("Total Games:")
        self.total_value = QLabel("0")
        self.total_value.setStyleSheet("color: #c5cee0;")
        stats_grid.addWidget(total_label, 0, 0)
        stats_grid.addWidget(self.total_value, 0, 1)
        
        win_rate_label = QLabel("Win Rate:")
        self.win_rate_value = QLabel("0%")
        self.win_rate_value.setStyleSheet("color: #4CAF50;")
        stats_grid.addWidget(win_rate_label, 1, 0)
        stats_grid.addWidget(self.win_rate_value, 1, 1)
        
        streak_label = QLabel("Current Streak:")
        self.streak_value = QLabel("-")
        self.streak_value.setStyleSheet("color: #c5cee0;")
        stats_grid.addWidget(streak_label, 2, 0)
        stats_grid.addWidget(self.streak_value, 2, 1)
        
        # Right column stats
        predictions_label = QLabel("Predictions:")
        self.predictions_value = QLabel("0")
        self.predictions_value.setStyleSheet("color: #c5cee0;")
        stats_grid.addWidget(predictions_label, 0, 2)
        stats_grid.addWidget(self.predictions_value, 0, 3)
        
        accuracy_label = QLabel("Accuracy:")
        self.accuracy_value = QLabel("0%")
        self.accuracy_value.setStyleSheet("color: #c5cee0;")
        stats_grid.addWidget(accuracy_label, 1, 2)
        stats_grid.addWidget(self.accuracy_value, 1, 3)
        
        best_pattern_label = QLabel("Best Pattern:")
        self.best_pattern_value = QLabel("-")
        self.best_pattern_value.setStyleSheet("color: #c5cee0;")
        stats_grid.addWidget(best_pattern_label, 2, 2)
        stats_grid.addWidget(self.best_pattern_value, 2, 3)
        
        stats_layout.addLayout(stats_grid)
        prediction_layout.addWidget(stats_frame)
        
        # Tab 2: History
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        history_layout.setContentsMargins(8, 8, 8, 8)
        
        history_frame = QFrame()
        history_frame.setObjectName("content")
        history_inner_layout = QVBoxLayout(history_frame)
        
        history_header = QLabel("RESULTS HISTORY")
        history_header.setObjectName("header")
        history_inner_layout.addWidget(history_header)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("border: none;")
        history_inner_layout.addWidget(self.results_display)
        
        history_layout.addWidget(history_frame)
        
        # Tab 3: Analysis
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setContentsMargins(8, 8, 8, 8)
        
        analysis_scroll = QScrollArea()
        analysis_scroll.setWidgetResizable(True)
        analysis_scroll.setFrameShape(QFrame.NoFrame)
        
        analysis_content = QWidget()
        analysis_content_layout = QVBoxLayout(analysis_content)
        analysis_content_layout.setContentsMargins(0, 0, 0, 0)
        analysis_content_layout.setSpacing(8)
        
        # Pattern analysis frame
        pattern_frame = QFrame()
        pattern_frame.setObjectName("content")
        pattern_layout = QVBoxLayout(pattern_frame)
        
        pattern_header = QLabel("PATTERN ANALYSIS")
        pattern_header.setObjectName("header")
        pattern_layout.addWidget(pattern_header)
        
        self.pattern_text = QTextEdit()
        self.pattern_text.setReadOnly(True)
        self.pattern_text.setStyleSheet("border: none;")
        self.pattern_text.setMaximumHeight(150)
        pattern_layout.addWidget(self.pattern_text)
        
        analysis_content_layout.addWidget(pattern_frame)
        
        # Matrix analysis frame
        matrix_frame = QFrame()
        matrix_frame.setObjectName("content")
        matrix_layout = QVBoxLayout(matrix_frame)
        
        matrix_header = QLabel("MATRIX ANALYSIS")
        matrix_header.setObjectName("header")
        matrix_layout.addWidget(matrix_header)
        
        self.matrix_text = QTextEdit()
        self.matrix_text.setReadOnly(True)
        self.matrix_text.setStyleSheet("border: none;")
        self.matrix_text.setMaximumHeight(150)
        matrix_layout.addWidget(self.matrix_text)
        
        analysis_content_layout.addWidget(matrix_frame)
        
        # Adaptive analysis frame
        adaptive_frame = QFrame()
        adaptive_frame.setObjectName("content")
        adaptive_layout = QVBoxLayout(adaptive_frame)
        
        adaptive_header = QLabel("ADAPTIVE ANALYSIS")
        adaptive_header.setObjectName("header")
        adaptive_layout.addWidget(adaptive_header)
        
        self.adaptive_text = QTextEdit()
        self.adaptive_text.setReadOnly(True)
        self.adaptive_text.setStyleSheet("border: none;")
        self.adaptive_text.setMaximumHeight(150)
        adaptive_layout.addWidget(self.adaptive_text)
        
        analysis_content_layout.addWidget(adaptive_frame)
        
        analysis_scroll.setWidget(analysis_content)
        analysis_layout.addWidget(analysis_scroll)
        
        # Add tabs to the tab widget
        self.tab_widget.addTab(prediction_tab, "PREDICTION")
        self.tab_widget.addTab(history_tab, "HISTORY")
        self.tab_widget.addTab(analysis_tab, "ANALYSIS")
        
        # Create a layout for the right panel
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.tab_widget)
        
        # Add right panel to main layout
        main_layout.addWidget(right_panel)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("background-color: #16213e; color: #a0a7c6;")
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready. Click 'WIN' or 'LOSS' to start recording results.")
        
        # Initialize display
        self.update_display()
        self.show()
    
    def change_algorithm(self, index):
        # Changes the active prediction algorithm
        algorithms = ["pattern", "matrix", "adaptive", "combined"]
        self.active_algorithm = algorithms[index]
        self.statusBar.showMessage(f"Algorithm changed to: {self.algo_combo.currentText()}")
        self.update_prediction()

    def update_significance_threshold(self, value):
        """Updates the minimum sample threshold"""
        self.significance_threshold = value
        self.statusBar.showMessage(f"Minimum sample size updated to {value}")
        self.analyze_data()
    
    def predict_next_pattern(self, history):
        """Makes pattern-based prediction"""
        max_pattern_length = self.pattern_spin.value()
        if len(history) < 3 or not self.pattern_stats:
            return None
        
        best_strat = None
        max_prob = 0
        max_samples = 0
        
        # Check from longest pattern
        for length in range(min(max_pattern_length, len(history)), 0, -1):
            current_pattern = ''.join(history[-length:])
            
            if current_pattern in self.pattern_stats:
                stats = self.pattern_stats[current_pattern]
                if stats["total"] >= self.significance_threshold:
                    current_prob = max(stats["win_prob"], stats["loss_prob"])
                    if current_prob > max_prob or (current_prob == max_prob and stats["total"] > max_samples):
                        max_prob = current_prob
                        max_samples = stats["total"]
                        best_strat = {
                            "target": "W" if stats["win_prob"] > stats["loss_prob"] else "L",
                            "prob": current_prob,
                            "pattern": current_pattern,
                            "samples": stats["total"],
                            "type": "Pattern"
                        }
        
        return best_strat
    
    def predict_next_matrix(self, history):
        # Makes matrix-based prediction
        if len(history) < 10 or not self.matrix_stats:
            return None
        
        # Last 10 results' matrix positions
        positions = []
        for i in range(min(10, len(history))):
            pos = (i % 5, i // 5)  # (row, column)
            positions.append((pos, history[-(i+1)]))  # Recent results first
        
        best_strat = None
        max_prob = 0
        
        # Predict based on matrix positions
        for matrix_key, stats in self.matrix_stats.items():
            # Ensure 'total' key exists
            if 'total' not in stats:
                pattern = stats.get('pattern', '')
                if pattern:
                    w_count = pattern.count('W')
                    l_count = pattern.count('L')
                    total = w_count + l_count
                    win_prob = (w_count / total * 100) if total > 0 else 0
                    loss_prob = (l_count / total * 100) if total > 0 else 0
                    
                    # Add required values
                    stats['total'] = total
                    stats['win_prob'] = win_prob
                    stats['loss_prob'] = loss_prob
                else:
                    # Skip if no pattern
                    continue
            
            # Check significance threshold
            if stats["total"] >= self.significance_threshold:
                current_prob = max(stats.get("win_prob", 0), stats.get("loss_prob", 0))
                if current_prob > max_prob:
                    max_prob = current_prob
                    target = "W" if stats.get("win_prob", 0) > stats.get("loss_prob", 0) else "L"
                    best_strat = {
                        "target": target,
                        "prob": current_prob,
                        "pattern": matrix_key,
                        "samples": stats["total"],
                        "type": "Matrix"
                    }
        
        return best_strat
    
    def predict_next_adaptive(self, history):
        # Makes adaptive (weighted) prediction
        if len(history) < 5 or not self.adaptive_stats:
            return None
        
        # Use last 50 results (or all if fewer)
        recent_window = min(50, len(history))
        recent_history = history[-recent_window:]
        
        # Count Ws and Ls
        w_count = recent_history.count('W')
        l_count = recent_history.count('L')
        
        # Trend analysis
        trend = None
        if w_count > l_count * 1.5:
            trend = "Yukselis"
        elif l_count > w_count * 1.5:
            trend = "Dusus"
        else:
            trend = "Denge"
        
        # Last 3 and last 7 results
        last_3 = ''.join(history[-3:]) if len(history) >= 3 else None
        last_7 = ''.join(history[-7:]) if len(history) >= 7 else None
        
        # Calculate W and L probabilities
        w_prob = 0
        l_prob = 0
        
        # Weight by trend
        if trend in self.adaptive_stats:
            trend_stats = self.adaptive_stats[trend]
            if trend_stats["total"] >= self.significance_threshold:
                w_prob += trend_stats["win_prob"] * 0.3  # 30% weight
                l_prob += trend_stats["loss_prob"] * 0.3
        
        # Weight by recent patterns
        if last_3 in self.pattern_stats:
            pattern_stats = self.pattern_stats[last_3]
            if pattern_stats["total"] >= self.significance_threshold:
                w_prob += pattern_stats["win_prob"] * 0.4  # 40% weight
                l_prob += pattern_stats["loss_prob"] * 0.4
        
        # Weight by longer pattern (if available)
        if last_7 in self.pattern_stats:
            pattern_stats = self.pattern_stats[last_7]
            if pattern_stats["total"] >= self.significance_threshold:
                w_prob += pattern_stats["win_prob"] * 0.3  # 30% weight
                l_prob += pattern_stats["loss_prob"] * 0.3
        
        # Make prediction if probability is over 50%
        if max(w_prob, l_prob) > 50:
            return {
                "target": "W" if w_prob > l_prob else "L",
                "prob": max(w_prob, l_prob),
                "pattern": f"{trend} + last pattern",
                "samples": self.adaptive_stats.get(trend, {"total": 0})["total"],
                "type": "Adaptive"
            }
        
        return None
        
        # Use last 50 results (or all if fewer)
        recent_window = min(50, len(history))
        recent_history = history[-recent_window:]
        
        # Count Ws and Ls
        w_count = recent_history.count('W')
        l_count = recent_history.count('L')
        
        # Trend analysis
        trend = None
        if w_count > l_count * 1.5:
            trend = "Yukselis"
        elif l_count > w_count * 1.5:
            trend = "Dusus"
        else:
            trend = "Denge"
        
        # Last 3 and last 7 results
        last_3 = ''.join(history[-3:]) if len(history) >= 3 else None
        last_7 = ''.join(history[-7:]) if len(history) >= 7 else None
        
        # Calculate W and L probabilities
        w_prob = 0
        l_prob = 0
        
        # Weight by trend
        if trend in self.adaptive_stats:
            trend_stats = self.adaptive_stats[trend]
            if trend_stats["total"] >= self.significance_threshold:
                w_prob += trend_stats["win_prob"] * 0.3  # 30% weight
                l_prob += trend_stats["loss_prob"] * 0.3
        
        # Weight by recent patterns
        if last_3 in self.pattern_stats:
            pattern_stats = self.pattern_stats[last_3]
            if pattern_stats["total"] >= self.significance_threshold:
                w_prob += pattern_stats["win_prob"] * 0.4  # 40% weight
                l_prob += pattern_stats["loss_prob"] * 0.4
        
        # Weight by longer pattern (if available)
        if last_7 in self.pattern_stats:
            pattern_stats = self.pattern_stats[last_7]
            if pattern_stats["total"] >= self.significance_threshold:
                w_prob += pattern_stats["win_prob"] * 0.3  # 30% weight
                l_prob += pattern_stats["loss_prob"] * 0.3
        
        # Make prediction if probability is over 50%
        if max(w_prob, l_prob) > 50:
            return {
                "target": "W" if w_prob > l_prob else "L",
                "prob": max(w_prob, l_prob),
                "pattern": f"{trend} + last pattern",
                "samples": self.adaptive_stats.get(trend, {"total": 0})["total"],
                "type": "Adaptive"
            }
        
        return None
        
        # Use last 50 results (or all if fewer)
        recent_window = min(50, len(history))
        recent_history = history[-recent_window:]
        
        # Count Ws and Ls
        w_count = recent_history.count('W')
        l_count = recent_history.count('L')
        
        # Trend analysis
        trend = None
        if w_count > l_count * 1.5:
            trend = "Yukselis"
        elif l_count > w_count * 1.5:
            trend = "Dusus"
        else:
            trend = "Denge"
        
        # Last 3 and last 7 results
        last_3 = ''.join(history[-3:]) if len(history) >= 3 else None
        last_7 = ''.join(history[-7:]) if len(history) >= 7 else None
        
        # Calculate W and L probabilities
        w_prob = 0
        l_prob = 0
        
        # Weight by trend
        if trend in self.adaptive_stats:
            trend_stats = self.adaptive_stats[trend]
            if trend_stats["total"] >= self.significance_threshold:
                w_prob += trend_stats["win_prob"] * 0.3  # 30% weight
                l_prob += trend_stats["loss_prob"] * 0.3
        
        # Weight by recent patterns
        if last_3 in self.pattern_stats:
            pattern_stats = self.pattern_stats[last_3]
            if pattern_stats["total"] >= self.significance_threshold:
                w_prob += pattern_stats["win_prob"] * 0.4  # 40% weight
                l_prob += pattern_stats["loss_prob"] * 0.4
        
        # Weight by longer pattern (if available)
        if last_7 in self.pattern_stats:
            pattern_stats = self.pattern_stats[last_7]
            if pattern_stats["total"] >= self.significance_threshold:
                w_prob += pattern_stats["win_prob"] * 0.3  # 30% weight
                l_prob += pattern_stats["loss_prob"] * 0.3
        
        # Make prediction if probability is over 50%
        if max(w_prob, l_prob) > 50:
            return {
                "target": "W" if w_prob > l_prob else "L",
                "prob": max(w_prob, l_prob),
                "pattern": f"{trend} + last pattern",
                "samples": self.adaptive_stats.get(trend, {"total": 0})["total"],
                "type": "Adaptive"
            }
        
        return None
    
    def predict_next(self, history):
        # Makes a prediction based on the active algorithm
        if len(history) < 3:
            return None
            
        # Use the specific prediction method based on active algorithm
        if self.active_algorithm == "pattern":
            return self.predict_next_pattern(history)
        elif self.active_algorithm == "matrix":
            return self.predict_next_matrix(history)
        elif self.active_algorithm == "adaptive":
            return self.predict_next_adaptive(history)
        elif self.active_algorithm == "combined":
            # Get all predictions
            pattern_pred = self.predict_next_pattern(history)
            matrix_pred = self.predict_next_matrix(history)
            adaptive_pred = self.predict_next_adaptive(history)
            
            # Take the one with highest probability
            predictions = [p for p in [pattern_pred, matrix_pred, adaptive_pred] if p is not None]
            if not predictions:
                return None
            
            # Return prediction with highest probability and most samples
            return max(predictions, key=lambda x: (x["prob"], x["samples"]))
        
        return None
            
        # Use the specific prediction method based on active algorithm
        if self.active_algorithm == "pattern":
            return self.predict_next_pattern(history)
        elif self.active_algorithm == "matrix":
            return self.predict_next_matrix(history)
        elif self.active_algorithm == "adaptive":
            return self.predict_next_adaptive(history)
        elif self.active_algorithm == "combined":
            # Get all predictions
            pattern_pred = self.predict_next_pattern(history)
            matrix_pred = self.predict_next_matrix(history)
            adaptive_pred = self.predict_next_adaptive(history)
            
            # Take the one with highest probability
            predictions = [p for p in [pattern_pred, matrix_pred, adaptive_pred] if p is not None]
            if not predictions:
                return None
            
            # Return prediction with highest probability and most samples
            return max(predictions, key=lambda x: (x["prob"], x["samples"]))
        
        return None
        
        if self.active_algorithm == "pattern":
            return self.predict_next_pattern(history)
        elif self.active_algorithm == "matrix":
            return self.predict_next_matrix(history)
        elif self.active_algorithm == "adaptive":
            return self.predict_next_adaptive(history)
        elif self.active_algorithm == "combined":
            # Get all predictions
            pattern_pred = self.predict_next_pattern(history)
            matrix_pred = self.predict_next_matrix(history)
            adaptive_pred = self.predict_next_adaptive(history)
            
            # Take the one with highest probability
            predictions = [p for p in [pattern_pred, matrix_pred, adaptive_pred] if p is not None]
            if not predictions:
                return None
            
            # Return prediction with highest probability and most samples
            return max(predictions, key=lambda x: (x["prob"], x["samples"]))
        
        return None
    
    def update_prediction_stats(self, actual):
        """Updates prediction statistics after a new result"""
        # Ensure we have at least 3 results
        if len(self.results) < 3:
            return
        
        # Make a prediction
        predicted = self.predict_next(self.results[:-1])
        
        if predicted is None:
            return
        
        # Add to prediction history
        self.prediction_history.append((predicted["target"], actual))
        
        self.prediction_stats['total_predictions'] += 1
        
        if predicted["target"] == actual:
            self.prediction_stats['correct'] += 1
            self.prediction_stats['current_win_streak'] += 1
            self.prediction_stats['current_loss_streak'] = 0
            if self.prediction_stats['current_win_streak'] > self.prediction_stats['max_win_streak']:
                self.prediction_stats['max_win_streak'] = self.prediction_stats['current_win_streak']
        else:
            self.prediction_stats['incorrect'] += 1
            self.prediction_stats['current_loss_streak'] += 1
            self.prediction_stats['current_win_streak'] = 0
            if self.prediction_stats['current_loss_streak'] > self.prediction_stats['max_loss_streak']:
                self.prediction_stats['max_loss_streak'] = self.prediction_stats['current_loss_streak']
        
        # Add data for loss streak analysis
        if self.prediction_stats['current_loss_streak'] >= 3:
            self.loss_streak_predictions.append({
                "loss_streak": self.prediction_stats['current_loss_streak'],
                "pattern": predicted["pattern"],
                "algorithm": predicted["type"],
                "prob": predicted["prob"]
            })
    
    def update_stats_display(self):
        """Updates the statistics display"""
        if not self.results:
            self.total_value.setText("0")
            self.win_rate_value.setText("0%")
            self.streak_value.setText("-")
            self.predictions_value.setText("0")
            self.accuracy_value.setText("0%")
            self.best_pattern_value.setText("-")
            return
            
        total_games = len(self.results)
        wins = self.results.count('W')
        losses = self.results.count('L')
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        # Calculate result streaks
        current_consecutive_wins = 0
        max_consecutive_wins = 0
        current_consecutive_losses = 0
        max_consecutive_losses = 0
        
        for result in self.results:
            if result == 'W':
                current_consecutive_wins += 1
                current_consecutive_losses = 0
                if current_consecutive_wins > max_consecutive_wins:
                    max_consecutive_wins = current_consecutive_wins
            else:
                current_consecutive_losses += 1
                current_consecutive_wins = 0
                if current_consecutive_losses > max_consecutive_losses:
                    max_consecutive_losses = current_consecutive_losses
        
        # Prediction accuracy
        prediction_accuracy = 0
        if self.prediction_stats['total_predictions'] > 0:
            prediction_accuracy = (self.prediction_stats['correct'] / self.prediction_stats['total_predictions'] * 100)
        
        # Update displayed values
        self.total_value.setText(str(total_games))
        self.win_rate_value.setText(f"{win_rate:.1f}%")
        
        # Current streak
        if current_consecutive_wins > 0:
            self.streak_value.setText(f"{current_consecutive_wins}W")
            self.streak_value.setStyleSheet("color: #4CAF50;")
        elif current_consecutive_losses > 0:
            self.streak_value.setText(f"{current_consecutive_losses}L")
            self.streak_value.setStyleSheet("color: #F44336;")
        else:
            self.streak_value.setText("-")
            self.streak_value.setStyleSheet("color: #c5cee0;")
        
        self.predictions_value.setText(str(self.prediction_stats['total_predictions']))
        self.accuracy_value.setText(f"{prediction_accuracy:.1f}%")
        
        # Find best pattern
        best_pattern = "-"
        if self.pattern_stats:
            best_pattern_item = None
            best_probability = 0
            best_samples = 0
            
            for pattern, stats in self.pattern_stats.items():
                if stats["total"] >= self.significance_threshold:
                    probability = max(stats["win_prob"], stats["loss_prob"])
                    if probability > best_probability or (probability == best_probability and stats["total"] > best_samples):
                        best_probability = probability
                        best_samples = stats["total"]
                        outcome = "W" if stats["win_prob"] > stats["loss_prob"] else "L"
                        best_pattern_item = (pattern, outcome, probability)
            
            if best_pattern_item:
                pattern, outcome, probability = best_pattern_item
                best_pattern = f"{pattern} → {outcome}"
        
        self.best_pattern_value.setText(best_pattern)
    
    def update_recent_results(self):
        """Updates the visual display of recent results"""
        # Clear current grid
        for i in range(self.recent_grid.count()):
            item = self.recent_grid.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Show the last 20 results (or fewer if not available)
        results_to_show = min(20, len(self.results))
        if results_to_show == 0:
            return
            
        recent_results = self.results[-results_to_show:]
        
        # Create a grid of result squares (10 per row)
        row, col = 0, 0
        for result in recent_results:
            result_label = QLabel(result)
            result_label.setAlignment(Qt.AlignCenter)
            result_label.setFixedSize(18, 18)
            result_label.setStyleSheet(
                f"background-color: {'#2e7d32' if result == 'W' else '#c62828'}; "
                f"color: white; font-weight: bold; border-radius: 2px;"
            )
            self.recent_grid.addWidget(result_label, row, col)
            
            col += 1
            if col >= 10:
                col = 0
                row += 1
    
    def update_prediction(self):
        # Updates the prediction display
        if len(self.results) < 3:
            self.pattern_value_pred.setText("-")
            self.success_value_pred.setText("-")
            self.recommend_value_pred.setText("-")
            self.recommend_value_pred.setStyleSheet("color: #c5cee0; font-size: 12pt; font-weight: bold;")
            return
        
        # Get prediction based on current algorithm
        current_prediction = self.predict_next(self.results)
        
        # Find all QLabel widgets in the prediction grid that show the algorithm
        algorithm_names = {
            "pattern": "Pattern Analysis",
            "matrix": "Matrix Analysis", 
            "adaptive": "Adaptive Analysis",
            "combined": "Combined Analysis"
        }
        
        # Find all children of the window
        for widget in self.findChildren(QLabel):
            # Look for QLabels with "Algorithm:" text
            if widget.text() == "Algorithm:":
                parent = widget.parent()
                if parent:
                    # Find next QLabel in same row of grid layout
                    for w in parent.findChildren(QLabel):
                        if w != widget and "Analysis" in w.text():
                            # This is the algorithm value label
                            w.setText(algorithm_names.get(self.active_algorithm, "Pattern Analysis"))
        
        if current_prediction:
            self.pattern_value_pred.setText(current_prediction["pattern"])
            self.success_value_pred.setText(f"{current_prediction['prob']:.1f}% ({current_prediction['samples']} samples)")
            
            # Set the recommendation
            self.recommend_value_pred.setText(current_prediction["target"])
            if current_prediction["target"] == "W":
                self.recommend_value_pred.setStyleSheet("color: #4CAF50; font-size: 12pt; font-weight: bold;")
            else:
                self.recommend_value_pred.setStyleSheet("color: #F44336; font-size: 12pt; font-weight: bold;")
            return
        
        # Get prediction based on current algorithm
        current_prediction = self.predict_next(self.results)
        
        # Update algorithm display in prediction tab
        algorithm_names = {
            "pattern": "Pattern Analysis",
            "matrix": "Matrix Analysis", 
            "adaptive": "Adaptive Analysis",
            "combined": "Combined Analysis"
        }
        
        # Find all QLabel widgets that might be showing the algorithm info
        for child in self.findChildren(QLabel):
            if child.text() == "Algorithm:":
                # Find the sibling label that shows the algorithm value
                parent_layout = child.parent().layout()
                if parent_layout:
                    # Try to find the value label in the same row of grid layout
                    for i in range(parent_layout.count()):
                        item = parent_layout.itemAt(i)
                        if item and item.widget():
                            if isinstance(item.widget(), QLabel) and item.widget() != child:
                                # Update the algorithm name in the UI
                                item.widget().setText(algorithm_names.get(self.active_algorithm, "Pattern Analysis"))
                                break
        
        if current_prediction:
            self.pattern_value_pred.setText(current_prediction["pattern"])
            self.success_value_pred.setText(f"{current_prediction['prob']:.1f}% ({current_prediction['samples']} samples)")
            
            # Set the recommendation
            self.recommend_value_pred.setText(current_prediction["target"])
            if current_prediction["target"] == "W":
                self.recommend_value_pred.setStyleSheet("color: #4CAF50; font-size: 12pt; font-weight: bold;")
            else:
                self.recommend_value_pred.setStyleSheet("color: #F44336; font-size: 12pt; font-weight: bold;")
            return
        
        # Get prediction based on current algorithm
        current_prediction = self.predict_next(self.results)
        
        # Update algorithm display in prediction tab
        algorithm_names = {
            "pattern": "Pattern Analysis",
            "matrix": "Matrix Analysis", 
            "adaptive": "Adaptive Analysis",
            "combined": "Combined Analysis"
        }
        
        # Find all QLabel widgets that might be showing the algorithm info
        for child in self.findChildren(QLabel):
            if child.text() == "Algorithm:":
                # Find the sibling label that shows the algorithm value
                parent_layout = child.parent().layout()
                if parent_layout:
                    # Try to find the value label in the same row of grid layout
                    for i in range(parent_layout.count()):
                        item = parent_layout.itemAt(i)
                        if item and item.widget():
                            if isinstance(item.widget(), QLabel) and item.widget() != child:
                                # Update the algorithm name in the UI
                                item.widget().setText(algorithm_names.get(self.active_algorithm, "Pattern Analysis"))
                                break
        
        if current_prediction:
            self.pattern_value_pred.setText(current_prediction["pattern"])
            self.success_value_pred.setText(f"{current_prediction['prob']:.1f}% ({current_prediction['samples']} samples)")
            
            # Set the recommendation
            self.recommend_value_pred.setText(current_prediction["target"])
            if current_prediction["target"] == "W":
                self.recommend_value_pred.setStyleSheet("color: #4CAF50; font-size: 12pt; font-weight: bold;")
            else:
                self.recommend_value_pred.setStyleSheet("color: #F44336; font-size: 12pt; font-weight: bold;")
            return
        
        current_prediction = self.predict_next(self.results)
        
        if current_prediction:
            self.pattern_value_pred.setText(current_prediction["pattern"])
            self.success_value_pred.setText(f"{current_prediction['prob']:.1f}% ({current_prediction['samples']} samples)")
            
            # Set the recommendation
            self.recommend_value_pred.setText(current_prediction["target"])
            if current_prediction["target"] == "W":
                self.recommend_value_pred.setStyleSheet("color: #4CAF50; font-size: 12pt; font-weight: bold;")
            else:
                self.recommend_value_pred.setStyleSheet("color: #F44336; font-size: 12pt; font-weight: bold;")
        else:
            self.pattern_value_pred.setText("-")
            self.success_value_pred.setText("-")
            self.recommend_value_pred.setText("Insufficient data")
            self.recommend_value_pred.setStyleSheet("color: #c5cee0; font-size: 12pt; font-weight: bold;")
    
    def update_display(self):
        """Updates all UI elements"""
        self.update_stats_display()
        self.update_recent_results()
        self.update_prediction()
        
        # Update history display
        history_html = ""
        
        for i, result in enumerate(self.results):
            color = "#4CAF50" if result == "W" else "#F44336"
            history_html += f"<span style='color: {color}; font-weight: bold;'>{result}</span> "
            
            if (i + 1) % 10 == 0:
                history_html += "<br>"
        
        self.results_display.setHtml(history_html)
    
    def add_result(self, result):
        """Adds a new result and updates everything"""
        if len(self.results) >= 3:
            self.update_prediction_stats(result)
        
        self.results.append(result)
        self.update_display()
        self.analyze_data()
        
        self.statusBar.showMessage(f"Added {result}. Total results: {len(self.results)}")
    
    def add_bulk_results(self):
        """Adds multiple results from the bulk input field"""
        bulk_text = self.bulk_input.toPlainText().strip()
        if not bulk_text:
            self.statusBar.showMessage("Bulk input cannot be empty!")
            return
            
        bulk_results = bulk_text.upper().split()
        valid_results = [r for r in bulk_results if r in ['W', 'L']]
        
        if len(valid_results) != len(bulk_results):
            self.statusBar.showMessage("Invalid characters found! Use only W and L.")
            return
            
        # Show progress bar for large data sets
        if len(valid_results) > 50:
            self.progress_bar.setRange(0, len(valid_results))
            self.progress_bar.setValue(0)
        
        # Add each result one by one for prediction calculations
        for i, result in enumerate(valid_results):
            if len(self.results) >= 3:
                self.update_prediction_stats(result)
            
            self.results.append(result)
            
            # Update progress bar
            if len(valid_results) > 50 and i % (len(valid_results) // 50) == 0:
                self.progress_bar.setValue(i)
                QApplication.processEvents()  # Allow UI to update
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Update UI once
        self.update_display()
        self.analyze_data()
        self.bulk_input.clear()
        
        self.statusBar.showMessage(f"Added {len(valid_results)} results. Total: {len(self.results)}")
    
    def delete_last_result(self):
        """Deletes the last result"""
        if self.results:
            deleted = self.results.pop()
            
            # Also remove last prediction if it exists
            if self.prediction_history:
                last_prediction = self.prediction_history.pop()
                
                # Update prediction stats
                if last_prediction[0] == last_prediction[1]:  # Correct prediction
                    self.prediction_stats['correct'] -= 1
                else:  # Incorrect prediction
                    self.prediction_stats['incorrect'] -= 1
                    
                self.prediction_stats['total_predictions'] -= 1
                
                # Recalculate streaks (simplified)
                if self.prediction_stats['total_predictions'] > 0:
                    last_correct = 0
                    for pred, actual in reversed(self.prediction_history):
                        if pred == actual:
                            last_correct += 1
                        else:
                            break
                    self.prediction_stats['current_win_streak'] = last_correct
                else:
                    self.prediction_stats['current_win_streak'] = 0
                    self.prediction_stats['current_loss_streak'] = 0
            
            self.update_display()
            self.analyze_data()
            
            self.statusBar.showMessage(f"Deleted last result ({deleted})")
        else:
            self.statusBar.showMessage("No results to delete")
    
    def clear_all_results(self):
        """Clears all results and resets everything"""
        if self.results:
            self.results.clear()
            self.prediction_history.clear()
            self.loss_streak_predictions.clear()
            
            # Reset prediction stats
            self.prediction_stats = {
                'total_predictions': 0,
                'correct': 0,
                'incorrect': 0,
                'current_win_streak': 0,
                'max_win_streak': 0,
                'current_loss_streak': 0,
                'max_loss_streak': 0
            }
            
            self.update_display()
            self.clear_analysis()
            
            self.statusBar.showMessage("All results cleared")
        else:
            self.statusBar.showMessage("No results to clear")
    
    def clear_analysis(self):
        """Clears all analysis data"""
        self.pattern_text.setText("")
        self.matrix_text.setText("")
        self.adaptive_text.setText("")
        
        # Reset stored analysis data
        self.pattern_stats = {}
        self.matrix_stats = {}
        self.adaptive_stats = {}
    
    def analyze_patterns(self):
        """Analyzes patterns in the results"""
        self.pattern_stats = {}
        max_pattern_length = self.pattern_spin.value()
        
        if len(self.results) < 3:
            self.pattern_text.setText("Need at least 3 results for pattern analysis.")
            return
        
        # For each pattern length
        for pattern_length in range(1, min(max_pattern_length + 1, len(self.results))):
            # Look at each position in results
            for i in range(len(self.results) - 1):
                if i >= pattern_length:
                    pattern = ''.join(self.results[i-pattern_length:i])
                    next_result = self.results[i]
                    
                    if pattern not in self.pattern_stats:
                        self.pattern_stats[pattern] = {"W": 0, "L": 0}
                    
                    self.pattern_stats[pattern][next_result] += 1
        
        # Convert counts to probabilities
        for pattern, outcomes in self.pattern_stats.items():
            total = outcomes["W"] + outcomes["L"]
            win_rate = (outcomes["W"] / total * 100) if total > 0 else 0
            loss_rate = (outcomes["L"] / total * 100) if total > 0 else 0
            
            self.pattern_stats[pattern]["total"] = total
            self.pattern_stats[pattern]["win_prob"] = win_rate
            self.pattern_stats[pattern]["loss_prob"] = loss_rate
            self.pattern_stats[pattern]["win_count"] = outcomes["W"]
            self.pattern_stats[pattern]["loss_count"] = outcomes["L"]
        
        # Display pattern analysis
        pattern_html = "<style>table { border-collapse: collapse; } td, th { padding: 4px 8px; border: 1px solid #2d3154; }</style>"
        pattern_html += "<table width='100%'>"
        pattern_html += "<tr><th>Pattern</th><th>Total</th><th>W %</th><th>L %</th><th>Best</th></tr>"
        
        # Sort patterns by highest probability
        sorted_patterns = sorted(
            self.pattern_stats.items(),
            key=lambda x: (max(x[1]["win_prob"], x[1]["loss_prob"]), x[1]["total"]),
            reverse=True
        )
        
        # Show only patterns with enough samples
        for pattern, stats in sorted_patterns:
            if stats["total"] >= self.significance_threshold:
                best = "W" if stats["win_prob"] > stats["loss_prob"] else "L"
                best_prob = max(stats["win_prob"], stats["loss_prob"])
                
                pattern_html += f"""
                <tr>
                    <td>{pattern}</td>
                    <td>{stats["total"]}</td>
                    <td style='color: {'#4CAF50' if stats["win_prob"] > 55 else '#c5cee0'};'>
                        {stats["win_prob"]:.1f}%
                    </td>
                    <td style='color: {'#F44336' if stats["loss_prob"] > 55 else '#c5cee0'};'>
                        {stats["loss_prob"]:.1f}%
                    </td>
                    <td style='color: {'#4CAF50' if best == 'W' else '#F44336'}; font-weight: bold;'>
                        {best} ({best_prob:.1f}%)
                    </td>
                </tr>
                """
        
        pattern_html += "</table>"
        
        self.pattern_text.setHtml(pattern_html)
    
    def analyze_matrix(self):
        """Analyzes results in a matrix format"""
        if len(self.results) < 25:  # Need at least 5x5 matrix
            self.matrix_text.setText("Need at least 25 results for matrix analysis.")
            return
        
        # Matrix dimensions
        rows = 5
        cols = 5
        
        # Create matrix
        matrix = [[None for _ in range(cols)] for _ in range(rows)]
        
        # Fill matrix with last 25 results (or fewer if not available)
        matrix_size = min(rows * cols, len(self.results))
        recent_results = self.results[-matrix_size:]
        
        for i, result in enumerate(reversed(recent_results)):  # Most recent at top-left
            row = i % rows
            col = i // rows
            matrix[row][col] = result
        
        # Analyze patterns in matrix
        self.matrix_stats = {}
        
        # Horizontal rows
        for r in range(rows):
            if all(matrix[r][c] is not None for c in range(cols)):
                pattern = ''.join(matrix[r][c] for c in range(cols))
                w_count = pattern.count('W')
                l_count = pattern.count('L')
                total = w_count + l_count
                win_prob = (w_count / total * 100) if total > 0 else 0
                loss_prob = (l_count / total * 100) if total > 0 else 0
                
                self.matrix_stats[f"H{r+1}:{pattern}"] = {
                    "row": r, 
                    "pattern": pattern,
                    "total": total,
                    "win_prob": win_prob,
                    "loss_prob": loss_prob
                }
        
        # Vertical columns
        for c in range(cols):
            if all(matrix[r][c] is not None for r in range(rows)):
                pattern = ''.join(matrix[r][c] for r in range(rows))
                w_count = pattern.count('W')
                l_count = pattern.count('L')
                total = w_count + l_count
                win_prob = (w_count / total * 100) if total > 0 else 0
                loss_prob = (l_count / total * 100) if total > 0 else 0
                
                self.matrix_stats[f"V{c+1}:{pattern}"] = {
                    "col": c, 
                    "pattern": pattern,
                    "total": total,
                    "win_prob": win_prob,
                    "loss_prob": loss_prob
                }
        
        # Display matrix visualization
        matrix_html = "<style>table { border-collapse: collapse; } td, th { padding: 4px 8px; border: 1px solid #2d3154; }</style>"
        
        # Matrix table
        matrix_html += "<table border='1'>"
        for row in matrix:
            matrix_html += "<tr>"
            for cell in row:
                if cell == 'W':
                    matrix_html += "<td style='background-color: #2e7d32; color: white; font-weight: bold;'>W</td>"
                elif cell == 'L':
                    matrix_html += "<td style='background-color: #c62828; color: white; font-weight: bold;'>L</td>"
                else:
                    matrix_html += "<td style='background-color: #1d203a;'>-</td>"
            matrix_html += "</tr>"
        matrix_html += "</table><br>"
        
        # Matrix pattern statistics
        matrix_html += "<table width='100%'>"
        matrix_html += "<tr><th>Position</th><th>Pattern</th><th>Best</th><th>Probability</th></tr>"
        
        for key, stats in self.matrix_stats.items():
            win_prob = stats.get("win_prob", 0)
            loss_prob = stats.get("loss_prob", 0)
            best = "W" if win_prob > loss_prob else "L"
            best_prob = max(win_prob, loss_prob)
            
            matrix_html += f"""
            <tr>
                <td>{key.split(':')[0]}</td>
                <td>{stats['pattern']}</td>
                <td style='color: {'#4CAF50' if best == 'W' else '#F44336'}; font-weight: bold;'>{best}</td>
                <td>{best_prob:.1f}%</td>
            </tr>
            """
        matrix_html += "</table>"
        
        self.matrix_text.setHtml(matrix_html)
    
    def analyze_adaptive(self):
        """Performs adaptive analysis"""
        if len(self.results) < 20:
            self.adaptive_text.setText("Need at least 20 results for adaptive analysis.")
            return
        
        # Analyze trends in different window sizes
        window_sizes = [10, 20, 50]
        trend_stats = {}
        
        for size in window_sizes:
            if len(self.results) >= size:
                # Look at each window
                for i in range(size, len(self.results) + 1):
                    window = self.results[i-size:i]
                    w_count = window.count("W")
                    l_count = window.count("L")
                    
                    # Determine trend type
                    if w_count / size >= 0.6:
                        trend_type = "Yukselis"  # Rising
                    elif l_count / size >= 0.6:
                        trend_type = "Dusus"  # Falling
                    else:
                        trend_type = "Denge"  # Balanced
                    
                    # Create key for this window size and trend
                    key = f"{size}_{trend_type}"
                    if key not in trend_stats:
                        trend_stats[key] = {"W": 0, "L": 0}
                    
                    # If there's a next result after this window, record it
                    if i < len(self.results):
                        next_result = self.results[i]
                        trend_stats[key][next_result] += 1
        
        # Convert to probabilities
        self.adaptive_stats = {}
        
        for key, outcomes in trend_stats.items():
            total = outcomes["W"] + outcomes["L"]
            if total >= self.significance_threshold:
                win_rate = (outcomes["W"] / total * 100) if total > 0 else 0
                loss_rate = (outcomes["L"] / total * 100) if total > 0 else 0
                
                # Extract trend information
                size, trend_type = key.split('_')
                
                self.adaptive_stats[trend_type] = {
                    "window": int(size),
                    "total": total,
                    "win_prob": win_rate,
                    "loss_prob": loss_rate,
                    "win_count": outcomes["W"],
                    "loss_count": outcomes["L"]
                }
        
        # Display adaptive analysis
        adaptive_html = "<style>table { border-collapse: collapse; } td, th { padding: 4px 8px; border: 1px solid #2d3154; }</style>"
        
        # Current trend
        if len(self.results) >= 10:
            last_10 = self.results[-10:]
            w_count = last_10.count("W")
            l_count = last_10.count("L")
            
            if w_count > l_count * 1.5:
                trend = "Yükseliş (Rising)"
                trend_color = "#4CAF50"
            elif l_count > w_count * 1.5:
                trend = "Düşüş (Falling)"
                trend_color = "#F44336"
            else:
                trend = "Denge (Balanced)"
                trend_color = "#FFC107"
            
            adaptive_html += f"<p>Current Trend: <span style='color: {trend_color}; font-weight: bold;'>{trend}</span></p>"
        
        # Trend analysis table
        adaptive_html += "<table width='100%'>"
        adaptive_html += "<tr><th>Trend Type</th><th>Total</th><th>W Prob.</th><th>L Prob.</th><th>Recommendation</th></tr>"
        
        for trend_type, stats in self.adaptive_stats.items():
            best = "W" if stats["win_prob"] > stats["loss_prob"] else "L"
            best_prob = max(stats["win_prob"], stats["loss_prob"])
            
            # Translate trend type
            if trend_type == "Yukselis":
                trend_name = "Rising"
            elif trend_type == "Dusus":
                trend_name = "Falling"
            else:
                trend_name = "Balanced"
            
            adaptive_html += f"""
            <tr>
                <td>{trend_name}</td>
                <td>{stats["total"]}</td>
                <td style='color: {'#4CAF50' if stats["win_prob"] > 55 else '#c5cee0'};'>
                    {stats["win_prob"]:.1f}%
                </td>
                <td style='color: {'#F44336' if stats["loss_prob"] > 55 else '#c5cee0'};'>
                    {stats["loss_prob"]:.1f}%
                </td>
                <td style='color: {'#4CAF50' if best == 'W' else '#F44336'}; font-weight: bold;'>
                    {best} ({best_prob:.1f}%)
                </td>
            </tr>
            """
            
        adaptive_html += "</table>"
        
        self.adaptive_text.setHtml(adaptive_html)
    
    def analyze_data(self):
        """Performs all analyses"""
        if len(self.results) < 3:
            return
        
        # Analyze patterns
        self.analyze_patterns()
        
        # Analyze matrix if enough data
        if len(self.results) >= 25:
            self.analyze_matrix()
        
        # Analyze adaptive trends if enough data
        if len(self.results) >= 20:
            self.analyze_adaptive()
    
    def load_results(self):
        """Loads results from a file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Results File", "", "Text Files (*.txt);;All Files (*)")
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                results = [r for r in content.upper().split() if r in ['W', 'L']]
                
                if not results:
                    self.statusBar.showMessage("No valid results found!")
                    return
                
                # Clear current results
                self.clear_all_results()
                
                # Add new results to bulk input and process
                self.bulk_input.setText(' '.join(results))
                self.add_bulk_results()
                
                self.statusBar.showMessage(f"Loaded {len(results)} results successfully.")
        
        except Exception as e:
            self.statusBar.showMessage(f"Error loading file: {str(e)}")
    
    def save_results(self):
        """Saves results to a file"""
        if not self.results:
            self.statusBar.showMessage("No results to save!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt);;All Files (*)")
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as file:
                file.write(' '.join(self.results))
            
            self.statusBar.showMessage(f"Saved {len(self.results)} results successfully.")
        
        except Exception as e:
            self.statusBar.showMessage(f"Error saving file: {str(e)}")


def main():
    app = QApplication(sys.argv)
    
    # Apply dark theme to entire application
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(26, 26, 46))
    dark_palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
    dark_palette.setColor(QPalette.Base, QColor(26, 26, 46))
    dark_palette.setColor(QPalette.AlternateBase, QColor(56, 56, 80))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(230, 230, 230))
    dark_palette.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    dark_palette.setColor(QPalette.Text, QColor(230, 230, 230))
    dark_palette.setColor(QPalette.Button, QColor(56, 56, 80))
    dark_palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(dark_palette)
    
    # Create and show the application
    ex = ModernBaccaratAnalyzer()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()