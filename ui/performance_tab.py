"""表現分析頁面"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLabel, QGroupBox, QPushButton, QComboBox)
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

class PerformanceTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("📈 組合表現分析 (Performance Analysis)")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Benchmark selection
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Benchmark:"))
        self.benchmark_combo = QComboBox()
        self.benchmark_combo.addItems(["SPY", "QQQ", "IWV", "VTI"])
        self.benchmark_combo.currentTextChanged.connect(self.update_display)
        controls.addWidget(self.benchmark_combo)
        
        refresh_btn = QPushButton("🔄 重新計算")
        refresh_btn.clicked.connect(self.update_display)
        controls.addWidget(refresh_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Metrics group
        metrics_group = QGroupBox("📉 關鍵指標")
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
        
        metrics_layout.addRow("📊 總回報:", self.total_return_label)
        metrics_layout.addRow("📈 年化回報:", self.annual_return_label)
        metrics_layout.addRow("💨 年化波動率:", self.volatility_label)
        metrics_layout.addRow("⭐ Sharpe Ratio:", self.sharpe_label)
        metrics_layout.addRow("🔺 Sortino Ratio:", self.sortino_label)
        metrics_layout.addRow("🔴 最大回撤:", self.max_dd_label)
        metrics_layout.addRow("⚠️ VaR (95%):", self.var_label)
        metrics_layout.addRow("🚨 CVaR (95%):", self.cvar_label)
        metrics_layout.addRow("🔹 Beta:", self.beta_label)
        metrics_layout.addRow("🎯 Alpha:", self.alpha_label)
        metrics_layout.addRow("📊 Benchmark 回報:", self.benchmark_return_label)
        
        layout.addWidget(metrics_group)
        
        # Chart
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def update_display(self):
        benchmark = self.benchmark_combo.currentText()
        
        # Get performance metrics
        metrics = self.main_window.performance_analyzer.get_performance_metrics(benchmark)
        
        if metrics is None:
            self.total_return_label.setText("N/A (無持倉數據)")
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
        
        # Update metrics labels
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
        
        # Plot cumulative returns
        self.plot_cumulative_returns(benchmark)
    
    def plot_cumulative_returns(self, benchmark):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get returns
        portfolio_returns = self.main_window.performance_analyzer.get_portfolio_returns()
        benchmark_returns = self.main_window.performance_analyzer.get_benchmark_returns(benchmark)
        
        if portfolio_returns.empty:
            ax.text(0.5, 0.5, '無持倉數據', 
                   ha='center', va='center', fontsize=14)
            self.canvas.draw()
            return
        
        # Calculate cumulative returns
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        
        ax.plot(portfolio_cumulative.index, (portfolio_cumulative - 1) * 100, 
               label='Hi5 Portfolio', linewidth=2, color='#4CAF50')
        
        if not benchmark_returns.empty:
            # Align indices
            aligned = pd.DataFrame({
                'portfolio': portfolio_returns,
                'benchmark': benchmark_returns
            }).dropna()
            
            benchmark_cumulative = (1 + aligned['benchmark']).cumprod()
            ax.plot(benchmark_cumulative.index, (benchmark_cumulative - 1) * 100,
                   label=f'{benchmark}', linewidth=2, color='#2196F3', alpha=0.7)
        
        ax.set_title('累計回報比較 (Cumulative Returns)', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=11)
        ax.set_ylabel('累計回報 (%)', fontsize=11)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        
        self.figure.tight_layout()
        self.canvas.draw()
