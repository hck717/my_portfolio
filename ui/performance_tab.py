"""Performance Analysis Tab with Date Range Selection"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLabel, QGroupBox, QPushButton, QComboBox, QDateEdit)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta

FigureCanvas = FigureCanvasQTAgg

plt.rcParams['font.sans-serif'] = ['Noto Sans CJK HK', 'Noto Sans CJK SC', 'Noto Sans CJK TC', 'Heiti TC', 'PingFang HK', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PerformanceTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.start_date = None
        self.end_date = None
        self.init_ui()
        self.set_default_date_range()
    
    def set_default_date_range(self):
        """Set default to 1 year"""
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        self.start_date = one_year_ago.strftime('%Y-%m-%d')
        self.end_date = today.strftime('%Y-%m-%d')
        
        self.start_date_edit.setDate(QDate.fromString(self.start_date, 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(self.end_date, 'yyyy-MM-dd'))
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Performance Analysis")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        controls = QHBoxLayout()
        
        controls.addWidget(QLabel("From:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.dateChanged.connect(self.on_date_changed)
        controls.addWidget(self.start_date_edit)
        
        controls.addWidget(QLabel("To:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.dateChanged.connect(self.on_date_changed)
        controls.addWidget(self.end_date_edit)
        
        preset_btns = QHBoxLayout()
        
        btn_1m = QPushButton("1M")
        btn_1m.clicked.connect(lambda: self.set_preset_range(30))
        preset_btns.addWidget(btn_1m)
        
        btn_3m = QPushButton("3M")
        btn_3m.clicked.connect(lambda: self.set_preset_range(90))
        preset_btns.addWidget(btn_3m)
        
        btn_6m = QPushButton("6M")
        btn_6m.clicked.connect(lambda: self.set_preset_range(180))
        preset_btns.addWidget(btn_6m)
        
        btn_1y = QPushButton("1Y")
        btn_1y.clicked.connect(lambda: self.set_preset_range(365))
        preset_btns.addWidget(btn_1y)
        
        btn_ytd = QPushButton("YTD")
        btn_ytd.clicked.connect(self.set_ytd_range)
        preset_btns.addWidget(btn_ytd)
        
        btn_all = QPushButton("ALL")
        btn_all.clicked.connect(self.set_all_range)
        preset_btns.addWidget(btn_all)
        
        controls.addLayout(preset_btns)
        
        controls.addWidget(QLabel("  Benchmark:"))
        self.benchmark_combo = QComboBox()
        self.benchmark_combo.addItems(["SPY", "QQQ", "IWV", "VTI", "SPTR"])
        self.benchmark_combo.currentTextChanged.connect(self.update_display)
        controls.addWidget(self.benchmark_combo)
        
        refresh_btn = QPushButton("Calculate")
        refresh_btn.setStyleSheet("font-weight: bold;")
        refresh_btn.clicked.connect(self.update_display)
        controls.addWidget(refresh_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        metrics_group = QGroupBox("Key Metrics")
        metrics_layout = QFormLayout()
        metrics_group.setLayout(metrics_layout)
        
        self.total_return_label = QLabel()
        self.annual_return_label = QLabel()
        self.volatility_label = QLabel()
        self.sharpe_label = QLabel()
        self.sortino_label = QLabel()
        self.max_dd_label = QLabel()
        self.var_label = QLabel()
        self.cvar_label = QLabel()
        self.beta_label = QLabel()
        self.alpha_label = QLabel()
        self.benchmark_return_label = QLabel()
        
        metrics_layout.addRow("Total Return:", self.total_return_label)
        metrics_layout.addRow("Annualized Return:", self.annual_return_label)
        metrics_layout.addRow("Volatility:", self.volatility_label)
        metrics_layout.addRow("Sharpe Ratio:", self.sharpe_label)
        metrics_layout.addRow("Sortino Ratio:", self.sortino_label)
        metrics_layout.addRow("Max Drawdown:", self.max_dd_label)
        metrics_layout.addRow("VaR (95%):", self.var_label)
        metrics_layout.addRow("CVaR (95%):", self.cvar_label)
        metrics_layout.addRow("Beta:", self.beta_label)
        metrics_layout.addRow("Alpha:", self.alpha_label)
        metrics_layout.addRow("Benchmark Return:", self.benchmark_return_label)
        
        layout.addWidget(metrics_group)
        
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def set_preset_range(self, days):
        """Set date range based on days"""
        today = datetime.now()
        start = today - timedelta(days=days)
        self.start_date = start.strftime('%Y-%m-%d')
        self.end_date = today.strftime('%Y-%m-%d')
        
        self.start_date_edit.setDate(QDate.fromString(self.start_date, 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(self.end_date, 'yyyy-MM-dd'))
        self.update_display()
    
    def set_ytd_range(self):
        """Set year-to-date range"""
        today = datetime.now()
        ytd = today.replace(month=1, day=1)
        self.start_date = ytd.strftime('%Y-%m-%d')
        self.end_date = today.strftime('%Y-%m-%d')
        
        self.start_date_edit.setDate(QDate.fromString(self.start_date, 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(self.end_date, 'yyyy-MM-dd'))
        self.update_display()
    
    def set_all_range(self):
        """Set maximum available range"""
        today = datetime.now()
        five_years_ago = today - timedelta(days=365*5)
        self.start_date = five_years_ago.strftime('%Y-%m-%d')
        self.end_date = today.strftime('%Y-%m-%d')
        
        self.start_date_edit.setDate(QDate.fromString(self.start_date, 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(self.end_date, 'yyyy-MM-dd'))
        self.update_display()
    
    def on_date_changed(self):
        """Handle date change"""
        self.start_date = self.start_date_edit.date().toString('yyyy-MM-dd')
        self.end_date = self.end_date_edit.date().toString('yyyy-MM-dd')
    
    def update_display(self):
        benchmark = self.benchmark_combo.currentText()
        
        self.start_date = self.start_date_edit.date().toString('yyyy-MM-dd')
        self.end_date = self.end_date_edit.date().toString('yyyy-MM-dd')
        
        metrics = self.main_window.performance_analyzer.get_performance_metrics(
            benchmark, self.start_date, self.end_date
        )
        
        if metrics is None:
            self.total_return_label.setText("N/A (No holdings)")
            self.annual_return_label.setText("N/A")
            self.volatility_label.setText("N/A")
            self.sharpe_label.setText("N/A")
            self.sortino_label.setText("N/A")
            self.max_dd_label.setText("N/A")
            self.var_label.setText("N/A")
            self.cvar_label.setText("N/A")
            self.beta_label.setText("N/A")
            self.alpha_label.setText("N/A")
            self.benchmark_return_label.setText("N/A")
            return
        
        self.total_return_label.setText(f"{metrics['total_return']*100:+.2f}%")
        self.annual_return_label.setText(f"{metrics['annualized_return']*100:+.2f}%")
        self.volatility_label.setText(f"{metrics['annualized_volatility']*100:.2f}%")
        self.sharpe_label.setText(f"{metrics['sharpe_ratio']:.3f}")
        self.sortino_label.setText(f"{metrics['sortino_ratio']:.3f}")
        self.max_dd_label.setText(f"{metrics['max_drawdown']*100:.2f}%")
        self.var_label.setText(f"{metrics['var_95']*100:.2f}%")
        self.cvar_label.setText(f"{metrics['cvar_95']*100:.2f}%")
        
        if 'beta' in metrics:
            self.beta_label.setText(f"{metrics['beta']:.3f}")
        else:
            self.beta_label.setText("N/A")
        
        if 'alpha' in metrics:
            self.alpha_label.setText(f"{metrics['alpha']*100:+.2f}%")
        else:
            self.alpha_label.setText("N/A")
        
        if 'benchmark_return' in metrics:
            self.benchmark_return_label.setText(f"{metrics['benchmark_return']*100:+.2f}%")
        else:
            self.benchmark_return_label.setText("N/A")
        
        self.plot_cumulative_returns(benchmark)
    
    def plot_cumulative_returns(self, benchmark):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        portfolio_returns = self.main_window.performance_analyzer.get_portfolio_returns(
            self.start_date, self.end_date
        )
        benchmark_returns = self.main_window.performance_analyzer.get_benchmark_returns(
            benchmark, self.start_date, self.end_date
        )
        
        if portfolio_returns.empty:
            ax.text(0.5, 0.5, 'No holdings data', 
                   ha='center', va='center', fontsize=14)
            self.canvas.draw()
            return
        
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        
        ax.plot(portfolio_cumulative.index, (portfolio_cumulative - 1) * 100, 
               label='Hi5 Portfolio', linewidth=2, color='#4CAF50')
        
        if not benchmark_returns.empty:
            aligned = pd.DataFrame({
                'portfolio': portfolio_returns,
                'benchmark': benchmark_returns
            }).dropna()
            
            if not aligned.empty:
                benchmark_cumulative = (1 + aligned['benchmark']).cumprod()
                ax.plot(benchmark_cumulative.index, (benchmark_cumulative - 1) * 100,
                       label=f'{benchmark}', linewidth=2, color='#2196F3', alpha=0.7)
        
        ax.set_title(f'Cumulative Returns ({self.start_date} to {self.end_date})', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Cumulative Return (%)', fontsize=11)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        
        self.figure.tight_layout()
        self.canvas.draw()
