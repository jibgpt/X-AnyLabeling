import json
from collections import defaultdict
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView, QSplitter, QWidget,
                             QTextEdit)


class GroupConsistencyDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.supported_shape = parent.supported_shape
        self.stats_data = {}
        self.output_dir = self.parent.output_dir
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("标签-GroupID一致性统计")
        self.resize(1400, 800)

        # 设置应用样式
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                gridline-color: #ebeef5;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid #ebeef5;
            }
            QTableWidget::item:selected {
                background-color: #ecf5ff;
                color: #409eff;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e1e4e8;
                font-weight: bold;
                color: #2c3e50;
            }
            QSplitter::handle {
                background-color: #dcdfe6;
                width: 1px;
            }
            QSplitter::handle:hover {
                background-color: #c0c4cc;
            }
        """)

        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # 顶部标题区域
        header_layout = QHBoxLayout()

        # 文件夹信息卡片
        folder_card = QWidget()
        folder_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
                padding: 12px 15px;
            }
        """)
        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setContentsMargins(10, 5, 10, 5)

        self.folder_label = QLabel(f"{self.output_dir}")
        self.folder_label.setStyleSheet("color: #2c3e50; font-size: 13px;")

        folder_layout.addWidget(self.folder_label)
        header_layout.addWidget(folder_card)

        # 分割器：左侧表格 + 右侧详情
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #dcdfe6; }")

        # 左侧：统计表格区域
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(15, 15, 15, 15)

        table_title = QLabel("标签统计")
        table_title.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 16px; margin-bottom: 10px;")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "标签", "标签数量", "GroupID数", "GroupID", "一致性状态"
        ])

        # 设置表格属性
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.show_details)

        # 设置列宽
        self.table.setColumnWidth(0, 450)  # 标签列
        self.table.setColumnWidth(1, 95)  # 实例总数
        self.table.setColumnWidth(2, 95)  # GroupID数
        self.table.setColumnWidth(3, 95)  # GroupID

        left_layout.addWidget(table_title)
        left_layout.addWidget(self.table)

        # 右侧：详情面板区域
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)

        details_title = QLabel("标签详情")
        details_title.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 16px; margin-bottom: 10px;")

        # 使用QTextEdit替代QLabel以获得更好的文本显示
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                background-color: #fafbfc;
            }
        """)
        self.details_text.setHtml("""
            <div style='color: #909399; text-align: center; padding: 40px;'>
                <p style='font-size: 16px; margin-bottom: 10px;'>👆</p>
                <p>双击左侧表格行查看标签详情</p>
            </div>
        """)

        right_layout.addWidget(details_title)
        right_layout.addWidget(self.details_text)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([1000, 400])  # 更合理的初始分割比例

        # 组装所有组件
        layout.addLayout(header_layout)
        layout.addWidget(splitter, 1)  # 给splitter分配更多空间

        # 分析数据并更新表格
        self.stats_data = self.analyze_label_group_consistency()
        self.update_table()
        self.exec_()

    def analyze_label_group_consistency(self):
        """分析当前文件夹下同标签的groupid一致性"""
        stats = defaultdict(lambda: {
            'total_instances': 0,
            'unique_groups': set(),
            'files_with_issues': defaultdict(list),
            'group_files': defaultdict(list),  # 新增：记录每个groupid对应的文件
            'consistency_status': 'consistent'
        })

        # 遍历文件夹中的所有JSON标注文件
        for file_path in Path(self.output_dir).rglob('*.json'):
            try:
                self.process_annotation_file(file_path, stats)
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")

        # 计算一致性状态
        for label, data in stats.items():
            if len(data['unique_groups']) > 1:
                data['consistency_status'] = 'inconsistent'
            else:
                data['consistency_status'] = 'consistent'

            # 转换set为list以便序列化
            data['unique_groups'] = list(data['unique_groups'])
            # 转换defaultdict为普通dict
            data['group_files'] = dict(data['group_files'])

        return dict(stats)

    def process_annotation_file(self, file_path, stats):
        """处理单个标注文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.process_json_annotations(data, str(file_path), stats)

    def process_json_annotations(self, data, filename, stats):
        """处理JSON格式的标注数据"""
        shapes = data.get('shapes', [])

        # 按标签分组统计groupid
        label_groups = defaultdict(set)

        for shape in shapes:
            label = shape.get('label', 'unknown')
            group_id = shape.get('group_id')

            if group_id is not None:
                label_groups[label].add(group_id)

                # 更新总体统计
                stats[label]['total_instances'] += 1
                stats[label]['unique_groups'].add(group_id)

                # 记录每个groupid对应的文件（去重）
                if filename not in stats[label]['group_files'][group_id]:
                    stats[label]['group_files'][group_id].append(filename)

        # 检查当前文件中的标签groupid一致性
        for label, groups in label_groups.items():
            if len(groups) > 1:
                stats[label]['files_with_issues'][filename].extend(list(groups))

    def update_table(self):
        """更新表格"""
        self.table.setRowCount(len(self.stats_data))

        for row, (label, data) in enumerate(self.stats_data.items()):
            # 标签名
            self.table.setItem(row, 0, QTableWidgetItem(label))

            # 实例总数
            self.table.setItem(row, 1, QTableWidgetItem(str(data['total_instances'])))

            # 唯一GroupID数
            unique_groupsnum = len(data['unique_groups'])
            self.table.setItem(row, 2, QTableWidgetItem(str(unique_groupsnum)))

            # 唯一GroupID
            unique_groups = data['unique_groups']
            self.table.setItem(row, 3, QTableWidgetItem(str(unique_groups)))

            # 一致性状态（带颜色显示）
            status_item = QTableWidgetItem(data['consistency_status'])
            if data['consistency_status'] == 'consistent':
                status_item.setBackground(QColor(144, 238, 144))  # 浅绿色
                status_item.setToolTip("该标签下所有实例的GroupID一致")
            else:
                status_item.setBackground(QColor(255, 182, 193))  # 浅红色
                status_item.setToolTip("该标签下存在不同的GroupID")
            self.table.setItem(row, 4, status_item)

    def show_details(self, index):
        """显示详情"""
        row = index.row()
        label = self.table.item(row, 0).text()

        if label not in self.stats_data:
            return

        label_stats = self.stats_data[label]

        # 构建详情文本
        details_text = f"""
        <h3>标签: {label}</h3>
        <b>标签数量:</b> {label_stats.get('total_instances', 0)}<br/>
        <b>GroupID数:</b> {len(label_stats.get('unique_groups', []))}<br/>
        <b>一致性状态:</b> {label_stats.get('consistency_status', 'unknown')}<br/>
        """

        if label_stats.get('unique_groups'):
            details_text += f"<b>所有GroupID:</b> {', '.join(map(str, label_stats['unique_groups']))}<br/><br/>"

            # 显示每个GroupID对应的前10个文件名
            details_text += "<h4>每个GroupID对应的文件:</h4>"
            for group_id in sorted(label_stats['unique_groups']):
                files = label_stats.get('group_files', {}).get(group_id, [])
                file_count = len(files)
                details_text += f"<b>GroupID {group_id}</b> (共 {file_count} 个文件):<br/>"

                # 显示前5个不同的文件名
                for i, file_path in enumerate(files[:10]):
                    file_name = Path(file_path).name
                    details_text += f"&nbsp;&nbsp;{i + 1}. {file_name}<br/>"

                if file_count > 10:
                    details_text += f"&nbsp;&nbsp;... 还有 {file_count - 10} 个文件<br/>"
                details_text += "<br/>"

        if label_stats.get('files_with_issues'):
            details_text += "<h4>有问题的文件（一个文件内该标签有多个GroupID）:</h4><ul>"
            for filename, groups in label_stats['files_with_issues'].items():
                details_text += f"<li>{Path(filename).name}: GroupIDs {list(groups)}</li>"
            details_text += "</ul>"

        self.details_text.setText(details_text)
