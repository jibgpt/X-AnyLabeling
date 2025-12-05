import shutil
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTextEdit)


class LeakageWrongCancelDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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

        self.image_output_dir1 = str(Path(self.parent.last_open_dir).parent / "hard" / "images")
        self.label_output_dir1 = str(Path(self.parent.last_open_dir).parent / "hard" / "json_labels")

        self.image_output_dir2 = str(Path(self.parent.last_open_dir).parent / "hard" / "误检" / "images")
        self.label_output_dir2 = str(Path(self.parent.last_open_dir).parent / "hard" / "误检" / "json_labels")

        self.image_output_dir3 = str(Path(self.parent.last_open_dir).parent / "hard" / "漏检" / "images")
        self.label_output_dir3 = str(Path(self.parent.last_open_dir).parent / "hard" / "漏检" / "json_labels")
        self.setup_ui()
        # 自动执行复制操作
        self.cancel()
        self.exec_()

    def setup_ui(self):
        self.setWindowTitle("撤销")
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


    def cancel(self):
        try:
            # 检查路径是否相等
            label_parent = str(Path(self.label_dir).parent)
            images_parent = str(Path(self.images_dir).parent)

            if label_parent != images_parent:
                error_message = f"❌ 路径不匹配，无法检查！\n"
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

            result_message = "全局检查结果:\n\n"

            # 获取当前文件的基本名（不带后缀）
            base_name = Path(self.label_path).stem

            # 处理三个输出目录
            directories_info = [
                ("hard 文件夹", self.image_output_dir1, self.label_output_dir1, "hard"),
                ("hard/误检 文件夹", self.image_output_dir2, self.label_output_dir2, "误检"),
                ("hard/漏检 文件夹", self.image_output_dir3, self.label_output_dir3, "漏检")
            ]

            # 检查并删除三个目录中的对应文件
            for dir_name, image_dir, label_dir, sub_dir_name in directories_info:
                # 检查图片文件是否存在
                image_file = Path(image_dir) / f"{base_name}.jpg"
                label_file = Path(label_dir) / f"{base_name}.json"

                deleted_files = []

                if image_file.exists():
                    image_file.unlink()
                    deleted_files.append(f"图片: {image_file.name}")

                if label_file.exists():
                    label_file.unlink()
                    deleted_files.append(f"标签: {label_file.name}")

                if deleted_files:
                    result_message += f"✅ 已从 {dir_name} 删除:\n"
                    for file in deleted_files:
                        result_message += f"   - {file}\n"
                    result_message += "\n"

            # 删除空目录（从内到外）
            result_message += "目录清理:\n"

            # 1. 先清理 images 和 json_labels 子目录
            sub_dirs_to_check = [
                (self.image_output_dir3, "漏检/images"),
                (self.label_output_dir3, "漏检/json_labels"),
                (self.image_output_dir2, "误检/images"),
                (self.label_output_dir2, "误检/json_labels"),
                (self.image_output_dir1, "hard/images"),
                (self.label_output_dir1, "hard/json_labels")
            ]

            for dir_path, dir_desc in sub_dirs_to_check:
                dir_obj = Path(dir_path)
                if dir_obj.exists() and dir_obj.is_dir():
                    # 检查目录是否为空
                    try:
                        if not any(dir_obj.iterdir()):
                            shutil.rmtree(dir_path)
                            result_message += f"✅ 已删除空目录: {dir_desc}\n"
                    except Exception as e:
                        result_message += f"⚠️ 删除目录 {dir_desc} 时出错: {str(e)}\n"

            # 2. 清理 误检 和 漏检 目录
            parent_dirs_to_check = [
                (Path(self.image_output_dir2).parent, "误检"),
                (Path(self.image_output_dir3).parent, "漏检")
            ]

            for dir_path, dir_desc in parent_dirs_to_check:
                if dir_path.exists() and dir_path.is_dir():
                    # 检查目录是否为空（包括可能的子目录）
                    try:
                        if not any(dir_path.iterdir()):
                            shutil.rmtree(str(dir_path))
                            result_message += f"✅ 已删除空目录: {dir_desc}\n"
                    except Exception as e:
                        result_message += f"⚠️ 删除目录 {dir_desc} 时出错: {str(e)}\n"

            # 3. 清理 hard 目录
            hard_dir = Path(self.image_output_dir1).parent
            if hard_dir.exists() and hard_dir.is_dir():
                try:
                    if not any(hard_dir.iterdir()):
                        shutil.rmtree(str(hard_dir))
                        result_message += f"✅ 已删除空目录: hard\n"
                    else:
                        # 检查 hard 目录下是否有文件（不包括子目录）
                        hard_contents = list(hard_dir.iterdir())
                        # 如果只剩下 .DS_Store 等隐藏文件，也可以考虑删除
                        if len(hard_contents) == 1 and hard_contents[0].name.startswith('.'):
                            shutil.rmtree(str(hard_dir))
                            result_message += f"✅ 已删除仅含隐藏文件的目录: hard\n"
                except Exception as e:
                    result_message += f"⚠️ 删除目录 hard 时出错: {str(e)}\n"

            # 如果没有执行任何操作，显示相应信息
            if result_message == "全局检查结果:\n\n目录清理:\n":
                result_message += "ℹ️ 没有找到需要清理的文件或目录\n"

            # 显示结果
            self.result_text.setText(result_message)
            self.result_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f0f9ff;
                    border: 2px solid #409eff;
                    border-radius: 8px;
                    font-size: 14px;
                    padding: 15px;
                    color: #333;
                }
            """)

        except Exception as e:
            error_message = f"❌ 过程中发生错误:\n{str(e)}"
            self.result_text.setText(error_message)
            self.result_text.setStyleSheet("""
                QTextEdit {
                    background-color: #fef0f0;
                    border: 2px solid #f56c6c;
                    border-radius: 8px;
                    font-size: 14px;
                    padding: 15px;
                    color: #f56c6c;
                }
            """)
