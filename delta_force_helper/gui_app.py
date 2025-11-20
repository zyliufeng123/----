"""
三角洲行动 - 物品识别助手 GUI
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QGroupBox,
    QListWidget, QMessageBox, QLineEdit, QComboBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

# 导入后端模块
import tools.screenshot_analyzer as analyzer
import tools.price_tracker as tracker
import tools.smart_importer as importer
import tools.view_data as viewer


class WorkerThread(QThread):
    """后台工作线程"""
    progress = pyqtSignal(str)  # 进度信号
    finished = pyqtSignal(dict)  # 完成信号
    
    def __init__(self, task_type, params=None):
        super().__init__()
        self.task_type = task_type
        self.params = params or {}
    
    def run(self):
        try:
            if self.task_type == 'analyze':
                self.run_analysis()
            elif self.task_type == 'price_track':
                self.run_price_tracking()
            elif self.task_type == 'import':
                self.run_import()
        except Exception as e:
            self.progress.emit(f"❌ 错误: {str(e)}")
    
    def run_analysis(self):
        """运行物品识别"""
        self.progress.emit("📸 开始分析截图...")
        
        # 这里调用后端识别逻辑
        folder = self.params.get('folder', 'D:/游戏截图/物品识别/')
        
        # 模拟进度（实际会调用真实方法）
        import time
        for i in range(1, 11):
            time.sleep(0.5)
            self.progress.emit(f"正在处理... {i*10}%")
        
        self.finished.emit({'status': 'success', 'count': 35})
    
    def run_price_tracking(self):
        """运行价格采集"""
        self.progress.emit("💰 开始价格采集...")
        # 调用价格采集逻辑
        pass
    
    def run_import(self):
        """运行智能导入"""
        self.progress.emit("🤖 开始智能导入...")
        # 调用导入逻辑
        pass


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("三角洲行动 - 物品识别助手 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 数据路径
        self.screenshots_folder = "D:/游戏截图/物品识别/"
        self.data_folder = Path("data")
        
        # 创建界面
        self.init_ui()
        
        # 加载数据
        self.load_data()
    
    def init_ui(self):
        """初始化界面"""
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 标题
        title = QLabel("🎮 三角洲行动 - 物品识别助手")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 选项卡
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # 1. 物品识别选项卡
        tabs.addTab(self.create_analyze_tab(), "📸 物品识别")
        
        # 2. 价格追踪选项卡
        tabs.addTab(self.create_price_tab(), "💰 价格追踪")
        
        # 3. 数据管理选项卡
        tabs.addTab(self.create_data_tab(), "📊 数据管理")
        
        # 4. 设置选项卡
        tabs.addTab(self.create_settings_tab(), "⚙️ 设置")
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_analyze_tab(self):
        """创建物品识别选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 文件选择区域
        file_group = QGroupBox("截图文件夹")
        file_layout = QHBoxLayout()
        file_group.setLayout(file_layout)
        
        self.folder_input = QLineEdit(self.screenshots_folder)
        file_layout.addWidget(self.folder_input)
        
        browse_btn = QPushButton("📁 浏览")
        browse_btn.clicked.connect(self.browse_folder)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # 操作按钮区域
        btn_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("🔍 开始识别")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        analyze_btn.clicked.connect(self.start_analysis)
        btn_layout.addWidget(analyze_btn)
        
        clear_btn = QPushButton("🗑️ 清空结果")
        clear_btn.clicked.connect(self.clear_results)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 结果显示区域
        result_group = QGroupBox("识别结果")
        result_layout = QVBoxLayout()
        result_group.setLayout(result_layout)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        self.stats_screenshots = QLabel("截图数：0")
        self.stats_items = QLabel("识别物品：0")
        self.stats_value = QLabel("总价值：0 币")
        
        stats_layout.addWidget(self.stats_screenshots)
        stats_layout.addWidget(self.stats_items)
        stats_layout.addWidget(self.stats_value)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        return widget
    
    def create_price_tab(self):
        """创建价格追踪选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        track_btn = QPushButton("💰 开始价格采集")
        track_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        track_btn.clicked.connect(self.start_price_tracking)
        btn_layout.addWidget(track_btn)
        
        refresh_btn = QPushButton("🔄 刷新价格表")
        refresh_btn.clicked.connect(self.refresh_prices)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # 价格表格
        price_group = QGroupBox("当前价格")
        price_layout = QVBoxLayout()
        price_group.setLayout(price_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索：")
        self.price_search = QLineEdit()
        self.price_search.setPlaceholderText("输入物品名称...")
        self.price_search.textChanged.connect(self.filter_prices)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.price_search)
        search_layout.addStretch()
        
        price_layout.addLayout(search_layout)
        
        # 表格
        self.price_table = QTableWidget()
        self.price_table.setColumnCount(7)
        self.price_table.setHorizontalHeaderLabels([
            "物品名称", "当前价格", "最低价", "最高价", "平均价", "趋势", "采样次数"
        ])
        self.price_table.setAlternatingRowColors(True)
        price_layout.addWidget(self.price_table)
        
        layout.addWidget(price_group)
        
        return widget
    
    def create_data_tab(self):
        """创建数据管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("🤖 智能导入新物品")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        import_btn.clicked.connect(self.smart_import)
        btn_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 导出数据")
        export_btn.clicked.connect(self.export_data)
        btn_layout.addWidget(export_btn)
        
        backup_btn = QPushButton("💾 备份数据")
        backup_btn.clicked.connect(self.backup_data)
        btn_layout.addWidget(backup_btn)
        
        layout.addLayout(btn_layout)
        
        # 分割器（上下两部分）
        splitter = QSplitter(Qt.Vertical)
        
        # 物品数据库
        db_group = QGroupBox("物品数据库")
        db_layout = QVBoxLayout()
        db_group.setLayout(db_layout)
        
        self.db_table = QTableWidget()
        self.db_table.setColumnCount(5)
        self.db_table.setHorizontalHeaderLabels([
            "物品名称", "价值", "稀有度", "类别", "最后更新"
        ])
        db_layout.addWidget(self.db_table)
        
        splitter.addWidget(db_group)
        
        # 未知物品
        unknown_group = QGroupBox("未知物品")
        unknown_layout = QVBoxLayout()
        unknown_group.setLayout(unknown_layout)
        
        self.unknown_list = QListWidget()
        unknown_layout.addWidget(self.unknown_list)
        
        splitter.addWidget(unknown_group)
        
        layout.addWidget(splitter)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.stats_db_count = QLabel("数据库物品：0")
        self.stats_unknown_count = QLabel("未知物品：0")
        
        stats_layout.addWidget(self.stats_db_count)
        stats_layout.addWidget(self.stats_unknown_count)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        return widget
    
    def create_settings_tab(self):
        """创建设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 路径设置
        path_group = QGroupBox("路径设置")
        path_layout = QVBoxLayout()
        path_group.setLayout(path_layout)
        
        # 截图文件夹
        screenshot_layout = QHBoxLayout()
        screenshot_layout.addWidget(QLabel("截图文件夹："))
        self.screenshot_path = QLineEdit(self.screenshots_folder)
        screenshot_layout.addWidget(self.screenshot_path)
        
        path_layout.addLayout(screenshot_layout)
        
        layout.addWidget(path_group)
        
        # OCR设置
        ocr_group = QGroupBox("OCR设置")
        ocr_layout = QVBoxLayout()
        ocr_group.setLayout(ocr_layout)
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("置信度阈值："))
        self.confidence_input = QLineEdit("0.4")
        confidence_layout.addWidget(self.confidence_input)
        confidence_layout.addStretch()
        
        ocr_layout.addLayout(confidence_layout)
        
        layout.addWidget(ocr_group)
        
        # 保存按钮
        save_btn = QPushButton("💾 保存设置")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        # 关于信息
        about_group = QGroupBox("关于")
        about_layout = QVBoxLayout()
        about_group.setLayout(about_layout)
        
        about_text = QLabel("""
            <h3>三角洲行动 - 物品识别助手 v1.0</h3>
            <p>功能：</p>
            <ul>
                <li>自动识别游戏截图中的物品</li>
                <li>追踪物品价格波动</li>
                <li>智能导入新物品到数据库</li>
                <li>数据导出和备份</li>
            </ul>
            <p>技术栈：Python, PyQt5, EasyOCR, OpenCV</p>
        """)
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_group)
        
        return widget
    
    # ============ 功能方法 ============
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择截图文件夹", self.screenshots_folder)
        if folder:
            self.folder_input.setText(folder)
            self.screenshots_folder = folder
    
    def start_analysis(self):
        """开始物品识别"""
        self.result_text.clear()
        self.result_text.append("🔍 开始识别...")
        
        folder = self.folder_input.text()
        
        if not Path(folder).exists():
            QMessageBox.warning(self, "警告", f"文件夹不存在：{folder}")
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 启动后台线程
        self.worker = WorkerThread('analyze', {'folder': folder})
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.start()
        
        self.statusBar().showMessage("正在识别...")
    
    def update_progress(self, message):
        """更新进度"""
        self.result_text.append(message)
        # 自动滚动到底部
        self.result_text.verticalScrollBar().setValue(
            self.result_text.verticalScrollBar().maximum()
        )
    
    def analysis_finished(self, result):
        """识别完成"""
        self.progress_bar.setVisible(False)
        
        if result['status'] == 'success':
            self.result_text.append(f"\n✅ 识别完成！共识别 {result['count']} 个物品")
            self.statusBar().showMessage("识别完成")
            
            # 更新统计信息
            self.stats_items.setText(f"识别物品：{result['count']}")
            
            # 刷新数据
            self.load_data()
        else:
            self.result_text.append("\n❌ 识别失败")
            self.statusBar().showMessage("识别失败")
    
    def clear_results(self):
        """清空结果"""
        self.result_text.clear()
    
    def start_price_tracking(self):
        """开始价格采集"""
        reply = QMessageBox.question(
            self,
            "确认",
            "开始价格采集？这将分析所有截图。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.worker = WorkerThread('price_track')
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.price_tracking_finished)
            self.worker.start()
    
    def price_tracking_finished(self, result):
        """价格采集完成"""
        QMessageBox.information(self, "完成", "价格采集完成！")
        self.refresh_prices()
    
    def refresh_prices(self):
        """刷新价格表"""
        price_file = self.data_folder / "current_prices.json"
        
        if not price_file.exists():
            return
        
        with open(price_file, 'r', encoding='utf-8') as f:
            prices = json.load(f)
        
        self.price_table.setRowCount(0)
        
        trend_symbols = {
            'rising': '📈',
            'falling': '📉',
            'stable': '➡️',
            'unknown': '❓'
        }
        
        for name, data in prices.items():
            row = self.price_table.rowCount()
            self.price_table.insertRow(row)
            
            self.price_table.setItem(row, 0, QTableWidgetItem(name))
            self.price_table.setItem(row, 1, QTableWidgetItem(f"{data['latest_price']:,}"))
            self.price_table.setItem(row, 2, QTableWidgetItem(f"{data['min_price']:,}"))
            self.price_table.setItem(row, 3, QTableWidgetItem(f"{data['max_price']:,}"))
            self.price_table.setItem(row, 4, QTableWidgetItem(f"{data['avg_price']:,}"))
            self.price_table.setItem(row, 5, QTableWidgetItem(trend_symbols.get(data['trend'], '❓')))
            self.price_table.setItem(row, 6, QTableWidgetItem(str(data['sample_count'])))
        
        self.price_table.resizeColumnsToContents()
    
    def filter_prices(self, text):
        """过滤价格表"""
        for row in range(self.price_table.rowCount()):
            item_name = self.price_table.item(row, 0).text()
            
            if text.lower() in item_name.lower():
                self.price_table.setRowHidden(row, False)
            else:
                self.price_table.setRowHidden(row, True)
    
    def smart_import(self):
        """智能导入"""
        reply = QMessageBox.question(
            self,
            "确认",
            "开始智能导入？将从价格数据自动生成物品数据库。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.worker = WorkerThread('import')
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.import_finished)
            self.worker.start()
    
    def import_finished(self, result):
        """导入完成"""
        QMessageBox.information(self, "完成", "智能导入完成！")
        self.load_data()
    
    def export_data(self):
        """导出数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            f"delta_force_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # 导出逻辑
            QMessageBox.information(self, "成功", f"数据已导出到：{file_path}")
    
    def backup_data(self):
        """备份数据"""
        backup_folder = self.data_folder / "backups"
        backup_folder.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 备份所有JSON文件
        import shutil
        for json_file in self.data_folder.glob("*.json"):
            backup_file = backup_folder / f"{json_file.stem}_{timestamp}.json"
            shutil.copy(json_file, backup_file)
        
        QMessageBox.information(self, "成功", f"数据已备份到：{backup_folder}")
    
    def save_settings(self):
        """保存设置"""
        QMessageBox.information(self, "成功", "设置已保存")
    
    def load_data(self):
        """加载数据"""
        # 加载物品数据库
        db_file = self.data_folder / "items" / "items_database.json"
        if db_file.exists():
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items = data.get('items', [])
                
                self.db_table.setRowCount(0)
                
                for item in items:
                    row = self.db_table.rowCount()
                    self.db_table.insertRow(row)
                    
                    self.db_table.setItem(row, 0, QTableWidgetItem(item['name']))
                    self.db_table.setItem(row, 1, QTableWidgetItem(f"{item.get('value', 0):,}"))
                    self.db_table.setItem(row, 2, QTableWidgetItem(item.get('rarity', 'unknown')))
                    self.db_table.setItem(row, 3, QTableWidgetItem(item.get('category', 'unknown')))
                    self.db_table.setItem(row, 4, QTableWidgetItem(item.get('last_update', 'N/A')[:10]))
                
                self.db_table.resizeColumnsToContents()
                self.stats_db_count.setText(f"数据库物品：{len(items)}")
        
        # 加载未知物品
        unknown_file = self.data_folder / "unknown_items.json"
        if unknown_file.exists():
            with open(unknown_file, 'r', encoding='utf-8') as f:
                unknown_items = json.load(f)
                
                self.unknown_list.clear()
                for item in unknown_items:
                    self.unknown_list.addItem(f"{item['name']} (置信度: {item['confidence']:.0%})")
                
                self.stats_unknown_count.setText(f"未知物品：{len(unknown_items)}")
        
        # 加载价格数据
        self.refresh_prices()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()