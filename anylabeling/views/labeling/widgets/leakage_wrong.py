import shutil
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTextEdit)


class LeakageWrongDialog(QtWidgets.QDialog):

    def __init__(self, parent, leakageWrongType=''):
        super().__init__(parent)
        self.parent = parent
        self.leakageWrongType = leakageWrongType
        self.supported_shape = parent.supported_shape
        self.stats_data = {}
        # C:/lable/瓶装_雪碧柠檬味汽水_500ml/321610111755862679979/main/json_labels
        self.label_dir = self.parent.output_dir
        # C:/lable/瓶装_雪碧柠檬味汽水_500ml/321610111755862679979/main/images
        self.images_dir = self.parent.last_open_dir
        # C:/lable/瓶装_雪碧柠檬味汽水_500ml/321610111755862679979/main/json_labels/0.json
        self.label_path = self.parent.label_file.filename
        # C:/lable/瓶装_雪碧柠檬味汽水_500ml/321610111755862679979/main/images/0.jpg
        self.image_path = self.parent.filename
        if leakageWrongType == '':
            self.image_output_dir = str(Path(self.parent.last_open_dir).parent / "hard" / "images")
            self.label_output_dir = str(Path(self.parent.last_open_dir).parent / "hard" / "json_labels")
        else:
            self.image_output_dir = str(Path(self.parent.last_open_dir).parent / "hard" / leakageWrongType / "images")
            self.label_output_dir = str(
                Path(self.parent.last_open_dir).parent / "hard" / leakageWrongType / "json_labels")
        self.setup_ui()
        # 自动执行复制操作
        self.copyImage()
        self.exec_()

    def setup_ui(self):
        if self.leakageWrongType == '':
            leakageWrongTypeMsg = "漏检-误检复制"
        else:
            leakageWrongTypeMsg = self.leakageWrongType + "复制"

        self.setWindowTitle(leakageWrongTypeMsg)
        self.resize(1600, 650)

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

        folder_label0 = QLabel(f"{leakageWrongTypeMsg}")
        folder_label0.setStyleSheet("color: #000080; font-size: 23px;")
        folder_layout.addWidget(folder_label0)

        folder_label1 = QLabel(f"当前图片: {self.image_path}")
        folder_label1.setStyleSheet("color: #ff0000; font-size: 23px;")
        folder_layout.addWidget(folder_label1)

        folder_label2 = QLabel(f"当前标签: {self.label_path}")
        folder_label2.setStyleSheet("color: #ff0000; font-size: 23px;")
        folder_layout.addWidget(folder_label2)

        folder_label3 = QLabel(f"图片输出: {self.image_output_dir}")
        folder_label3.setStyleSheet("color: #2c3e50; font-size: 23px;")
        folder_layout.addWidget(folder_label3)

        folder_label4 = QLabel(f"标签输出: {self.label_output_dir}")
        folder_label4.setStyleSheet("color: #2c3e50; font-size: 23px;")
        folder_layout.addWidget(folder_label4)

        header_layout.addWidget(folder_card)

        # 添加结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                font-size: 14px;
                padding: 15px;
            }
        """)

        # 添加关闭按钮
        button_layout = QHBoxLayout()
        self.close_button = QtWidgets.QPushButton("关闭")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #909399;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a6a9ad;
            }
            QPushButton:pressed {
                background-color: #82848a;
            }
        """)
        self.close_button.clicked.connect(self.close)

        button_layout.addWidget(self.close_button)
        button_layout.addStretch()

        # 组装所有组件
        layout.addLayout(header_layout)
        layout.addWidget(QLabel("操作结果:"))
        layout.addWidget(self.result_text)
        layout.addLayout(button_layout)

    def copyImage(self):
        """复制图片和标签到对应的位置并回显是否复制成功"""
        try:
            # 检查路径是否相等
            label_parent = str(Path(self.label_dir).parent)
            images_parent = str(Path(self.images_dir).parent)

            if label_parent != images_parent:
                error_message = f"❌ 路径不匹配，无法复制！\n"
                error_message += f"标签目录父级: {label_parent}\n"
                error_message += f"图片目录父级: {images_parent}\n"
                error_message += "请确保标签和图片目录在同一父级目录下"

                self.result_text.setText(error_message)
                self.result_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #fef0f0;
                        border: 2px solid #f56c6c;
                        border-radius: 8px;
                        font-size: 30px;
                        padding: 15px;
                        color: #f56c6c;
                    }
                """)
                return

            # 创建目标目录
            image_target_dir = Path(self.image_output_dir)
            label_target_dir = Path(self.label_output_dir)
            # 创建目录（如果不存在）
            image_target_dir.mkdir(parents=True, exist_ok=True)
            label_target_dir.mkdir(parents=True, exist_ok=True)

            # 获取源文件路径
            source_image_path = Path(self.image_path)
            source_label_path = Path(self.label_path)

            # 目标文件路径
            target_image_path = image_target_dir / source_image_path.name
            target_label_path = label_target_dir / source_label_path.name

            # 复制文件
            result_messages = []

            # 复制图片
            if source_image_path.exists():
                shutil.copy2(source_image_path, target_image_path)
                result_messages.append(f"✅ 图片复制成功: {target_image_path}")
            else:
                result_messages.append(f"❌ 图片文件不存在: {source_image_path}")

            # 复制标签
            if source_label_path.exists():
                shutil.copy2(source_label_path, target_label_path)
                result_messages.append(f"✅ 标签复制成功: {target_label_path}")
            else:
                result_messages.append(f"❌ 标签文件不存在: {source_label_path}")

            # 显示结果
            result_text = "\n".join(result_messages)
            self.result_text.setText(result_text)

            # 根据结果设置不同的样式
            if "❌" in result_text:
                self.result_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #fef0f0;
                        border: 2px solid #f56c6c;
                        border-radius: 8px;
                        font-size: 23px;
                        padding: 15px;
                        color: #f56c6c;
                    }
                """)
            else:
                self.result_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #f0f9ff;
                        border: 2px solid #409eff;
                        border-radius: 8px;
                        font-size: 23px;
                        padding: 15px;
                        color: #000080;
                    }
                """)

        except Exception as e:
            error_message = f"❌ 复制过程中发生错误:\n{str(e)}"
            self.result_text.setText(error_message)
            self.result_text.setStyleSheet("""
                QTextEdit {
                    background-color: #fef0f0;
                    border: 2px solid #f56c6c;
                    border-radius: 8px;
                    font-size: 30px;
                    padding: 15px;
                    color: #f56c6c;
                }
            """)
