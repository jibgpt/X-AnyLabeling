import shutil
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTextEdit)


class GlobalCheckDialog(QtWidgets.QDialog):

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
        # check，先判断
        self.check()
        self.exec_()

    def setup_ui(self):
        self.setWindowTitle("全局检查漏误检")
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

    def check(self):
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

            # 处理三个输出目录
            directories_info = [
                ("hard 文件夹", self.image_output_dir1, self.label_output_dir1, "hard"),
                ("hard/误检 文件夹", self.image_output_dir2, self.label_output_dir2, "误检"),
                ("hard/漏检 文件夹", self.image_output_dir3, self.label_output_dir3, "漏检")
            ]

            total_processed = 0
            total_images = 0

            for dir_name, img_dir_path, label_dir_path, subdir in directories_info:
                img_dir = Path(img_dir_path)
                label_dir = Path(label_dir_path)

                # 检查图片目录是否存在
                if not img_dir.exists():
                    result_message += f"⚠️ {dir_name}不存在: {img_dir}\n"
                    continue

                # 统计图片数量
                image_files = []
                for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.JPG', '.JPEG', '.PNG', '.BMP']:
                    image_files.extend(list(img_dir.glob(f'*{ext}')))

                image_count = len(image_files)
                total_images += image_count

                if image_count == 0:
                    result_message += f"📁 {dir_name} 存在，但没有图片文件\n"
                    continue

                # 创建对应的标签输出目录
                label_dir.mkdir(parents=True, exist_ok=True)

                # 遍历图片文件并复制对应的标签文件
                processed_count = 0
                for img_file in image_files:
                    # 获取不带扩展名的文件名
                    file_stem = img_file.stem

                    # 在源标签目录中查找对应的.json文件
                    source_label_file = Path(self.label_dir) / f"{file_stem}.json"

                    if source_label_file.exists():
                        # 目标标签文件路径
                        target_label_file = label_dir / f"{file_stem}.json"

                        try:
                            # 复制标签文件
                            shutil.copy2(source_label_file, target_label_file)
                            processed_count += 1
                            total_processed += 1
                        except Exception as e:
                            result_message += f"❌ 复制 {file_stem}.json 失败: {str(e)}\n"
                    else:
                        result_message += f"⚠️ 未找到 {file_stem}.json 标签文件\n"

                result_message += f"✅ {dir_name}:\n"
                result_message += f"   图片数量: {image_count}张\n"
                result_message += f"   成功复制标签: {processed_count}个\n"

                # 检查是否有图片没有对应的标签
                if processed_count < image_count:
                    result_message += f"   ⚠️ {image_count - processed_count}张图片没有对应的标签文件\n"

                result_message += "\n"

            # 汇总信息
            result_message += "=" * 50 + "\n"
            result_message += f"📊 汇总统计:\n"
            result_message += f"   总共发现: {total_images}张图片\n"
            result_message += f"   成功处理: {total_processed}个标签文件\n"

            if total_images > 0:
                result_message += f"   处理完成率: {(total_processed / total_images) * 100:.1f}%\n"

            self.result_text.setText(result_message)

            # 根据结果设置不同的样式
            if total_processed == 0:
                self.result_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #fff4e6;
                        border: 2px solid #ffa726;
                        border-radius: 8px;
                        font-size: 14px;
                        padding: 15px;
                        color: #e65100;
                    }
                """)
            else:
                self.result_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #f0f9eb;
                        border: 2px solid #67c23a;
                        border-radius: 8px;
                        font-size: 14px;
                        padding: 15px;
                        color: #2c3e50;
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
