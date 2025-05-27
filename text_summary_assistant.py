import sys
import os
import win32clipboard
import win32con
import win32gui
import win32api
import requests
import time
import markdown
import pyautogui
import keyboard
from dotenv import load_dotenv
from openai import OpenAI
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                           QWidget, QTextBrowser, QPushButton, QVBoxLayout, QLabel, QMessageBox,
                           QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QHBoxLayout,
                           QGraphicsDropShadowEffect)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QCursor
from PyQt6.QtCore import (Qt, QPoint, QSize, QThread, pyqtSignal, QTimer,
                         QMetaObject, Q_ARG, pyqtSlot)

# Load environment variables
load_dotenv()

class ClipboardThread(QThread):
    text_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            print("剪贴板线程开始运行")
            # Simulate Ctrl+C to copy selected text to clipboard
            keyboard.send('ctrl+c')
            # Wait a bit for the clipboard
            time.sleep(0.2)
            
            text = self.get_clipboard_text()
            if text:
                print(f"剪贴板线程获取到文本，准备发送信号")
                self.text_ready.emit(text)
                print("剪贴板线程已发送文本信号")
            else:
                print("剪贴板线程没有找到文本，发送错误信号")
                self.error.emit("没有找到选中的文本")
        except Exception as e:
            print(f"剪贴板线程出错: {str(e)}")
            self.error.emit(str(e))
        finally:
            print("剪贴板线程结束运行")

    def get_clipboard_text(self):
        try:
            win32clipboard.OpenClipboard()
            print("剪贴板已打开")
            
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                print(f"获取到Unicode文本，长度: {len(text)}")
                return text
            elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                print("获取到普通文本")
                if isinstance(text, bytes):
                    # Try different encodings
                    encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'ascii']
                    for encoding in encodings:
                        try:
                            decoded = text.decode(encoding)
                            print(f"使用 {encoding} 解码成功，长度: {len(decoded)}")
                            return decoded
                        except UnicodeDecodeError:
                            continue
                    # If all encodings fail, use 'ignore' option with utf-8
                    print("所有编码都失败，使用 utf-8 (ignore)")
                    decoded = text.decode('utf-8', errors='ignore')
                    print(f"解码后文本长度: {len(decoded)}")
                    return decoded
                return text
            print("剪贴板中没有文本")
            return ""
        finally:
            try:
                win32clipboard.CloseClipboard()
                print("剪贴板已关闭")
            except:
                pass

class SummarizeThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    chunk_received = pyqtSignal(str)  # New signal for streaming chunks

    def __init__(self, text, api_key, base_url):
        super().__init__()
        self.text = text
        self.api_key = api_key
        self.base_url = base_url
        self.full_response = ""

    def run(self):
        try:
            print("初始化 OpenAI 客户端")
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            print("开始调用API进行总结")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个文本总结助手，请简明扼要地总结用户提供的文本。"},
                    {"role": "user", "content": f"请总结以下文本：\n{self.text}"}
                ],
                stream=True  # Enable streaming
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    self.full_response += content
                    self.chunk_received.emit(self.full_response)
            
            print("API调用成功")
            self.finished.emit(self.full_response)
        except Exception as e:
            print(f"API调用失败: {str(e)}")
            self.error.emit(str(e))

class TranslateThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    chunk_received = pyqtSignal(str)  # Signal for streaming chunks

    def __init__(self, text, api_key, base_url, target_language):
        super().__init__()
        self.text = text
        self.api_key = api_key
        self.base_url = base_url
        self.target_language = target_language
        self.full_response = ""

    def run(self):
        try:
            print("初始化 OpenAI 客户端进行翻译")
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            print(f"开始调用API进行翻译到{self.target_language}")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"你是一个专业的翻译助手，请将用户提供的文本翻译成{self.target_language}。保持原文的格式和语气，确保翻译准确自然。"},
                    {"role": "user", "content": f"请将以下文本翻译成{self.target_language}：\n{self.text}"}
                ],
                stream=True  # Enable streaming
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    self.full_response += content
                    self.chunk_received.emit(self.full_response)
            
            print("翻译API调用成功")
            self.finished.emit(self.full_response)
        except Exception as e:
            print(f"翻译API调用失败: {str(e)}")
            self.error.emit(str(e))

class FloatingIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint | 
                          Qt.WindowType.Tool |
                          Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setup_ui()
        self.selected_text = ""
        self.parent_assistant = parent
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create icon label
        self.icon_label = QLabel()
        pixmap = QIcon("icon.png").pixmap(QSize(32, 32))
        if pixmap.isNull():
            print("警告：图标加载失败，使用默认文本")
            self.icon_label.setText("📝")
            self.icon_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 16px;
                    padding: 4px;
                }
                QLabel:hover {
                    background-color: rgba(200, 200, 255, 200);
                }
            """)
        else:
            print("图标加载成功")
            self.icon_label.setPixmap(pixmap)
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 16px;
                    padding: 4px;
                }
                QLabel:hover {
                    background-color: rgba(200, 200, 255, 200);
                }
            """)
        
        layout.addWidget(self.icon_label)
        self.setLayout(layout)
        self.resize(40, 40)
        
    def showEvent(self, event):
        super().showEvent(event)
        print("FloatingIcon.showEvent 被调用")
        self.raise_()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("图标被点击")
            self.show_action_menu(event.globalPosition().toPoint())
        elif event.button() == Qt.MouseButton.RightButton:
            print("右键点击图标，隐藏图标")
            self.hide()
    
    def show_action_menu(self, position):
        """Show action menu with summary and translation options"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #404040;
            }
            QMenu::icon {
                padding-left: 10px;
            }
        """)
        
        # Summary action
        summary_action = QAction("📊 AI 总结", menu)
        summary_action.triggered.connect(lambda: self.on_action_selected("summary"))
        menu.addAction(summary_action)
        
        # Translation action
        translate_action = QAction("🌐 翻译文本", menu)
        translate_action.triggered.connect(lambda: self.on_action_selected("translate"))
        menu.addAction(translate_action)
        
        # Show menu at position
        menu.exec(position)
        
    def on_action_selected(self, action):
        """Handle action selection"""
        self.hide()
        if hasattr(self, 'on_action_callback'):
            self.on_action_callback(self.selected_text, action)

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()
        self.current_summary = ""
        self.is_dragging = False
        self.drag_position = QPoint()
        self.current_mode = "summary"  # "summary" or "translate"

    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget with shadow effect
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333333;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.GlobalColor.black)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Create title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(45)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #404040;
            }
        """)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 0, 15, 0)
        
        # Title with icon
        title_icon_layout = QHBoxLayout()
        title_icon_layout.setSpacing(10)
        
        # Add icon
        self.icon_label = QLabel()
        icon_pixmap = QIcon("icon.png").pixmap(QSize(20, 20))
        if icon_pixmap.isNull():
            self.icon_label.setText("📝")
            self.icon_label.setStyleSheet("font-size: 18px;")
        else:
            self.icon_label.setPixmap(icon_pixmap)
        title_icon_layout.addWidget(self.icon_label)
        
        # Title text (will be updated dynamically)
        self.title_label = QLabel("AI 文本总结")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
        """)
        title_icon_layout.addWidget(self.title_label)
        title_icon_layout.addStretch()
        
        title_layout.addLayout(title_icon_layout)
        
        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        # Copy button
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(30, 30)
        self.copy_btn.setToolTip("复制总结内容")
        self.copy_btn.clicked.connect(self.copy_summary)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        controls_layout.addWidget(self.copy_btn)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c42b1c;
            }
        """)
        controls_layout.addWidget(close_btn)
        
        title_layout.addLayout(controls_layout)
        title_bar.setLayout(title_layout)
        container_layout.addWidget(title_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 20)
        
        # Status label for loading state
        self.status_label = QLabel("正在生成总结...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #58a6ff;
                font-size: 14px;
                font-style: italic;
                padding: 5px 0;
            }
        """)
        self.status_label.hide()
        content_layout.addWidget(self.status_label)
        
        # Create text display area using QTextBrowser
        self.text_display = QTextBrowser()
        self.text_display.setOpenExternalLinks(True)
        self.text_display.setStyleSheet("""
            QTextBrowser {
                background-color: #262626;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 15px;
                font-size: 15px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                line-height: 1.6;
                selection-background-color: #3a3a3a;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        content_layout.addWidget(self.text_display)
        
        content_widget.setLayout(content_layout)
        container_layout.addWidget(content_widget)
        
        # Set container layout
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Set initial size
        self.resize(500, 400)
        
        # Enable dragging
        title_bar.mousePressEvent = self.start_drag
        title_bar.mouseMoveEvent = self.do_drag
        title_bar.mouseReleaseEvent = self.stop_drag

    def start_drag(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def do_drag(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def stop_drag(self, event):
        self.is_dragging = False

    def copy_summary(self):
        """Copy summary content to clipboard"""
        if self.current_summary:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_summary)
            
            # Show feedback
            self.copy_btn.setText("✓")
            QTimer.singleShot(1000, lambda: self.copy_btn.setText("📋"))

    def update_summary(self, text):
        """Update the summary text with streaming content"""
        self.current_summary = text
        self.status_label.hide()
        self.show_summary(text, self.pos(), mode=self.current_mode)

    def show_summary(self, text, position=None, mode="summary"):
        # Set the mode first
        self.set_mode(mode)
        
        # Show loading state for initial message
        if "正在生成" in text or "正在翻译" in text:
            self.status_label.setText(text)
            self.status_label.show()
            self.text_display.clear()
        else:
            self.status_label.hide()
            
        # Convert Markdown to HTML with enhanced styling
        try:
            # Add custom CSS for dark theme with better typography
            css = """
            <style>
                body { 
                    color: #e0e0e0; 
                    font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                    line-height: 1.8;
                    margin: 0;
                    padding: 0;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #ffffff;
                    margin-top: 1em;
                    margin-bottom: 0.5em;
                    font-weight: 600;
                }
                h1 { font-size: 1.5em; border-bottom: 2px solid #404040; padding-bottom: 0.3em; }
                h2 { font-size: 1.3em; }
                h3 { font-size: 1.1em; }
                p { margin: 0.8em 0; }
                a { color: #58a6ff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                code { 
                    background-color: #333333; 
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 0.9em;
                }
                pre {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    padding: 12px;
                    border-radius: 6px;
                    overflow-x: auto;
                    margin: 1em 0;
                }
                pre code {
                    background-color: transparent;
                    padding: 0;
                }
                blockquote {
                    border-left: 4px solid #58a6ff;
                    margin: 1em 0;
                    padding-left: 1em;
                    color: #b0b0b0;
                    font-style: italic;
                }
                ul, ol {
                    margin: 0.8em 0;
                    padding-left: 2em;
                }
                li { margin: 0.3em 0; }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }
                th, td {
                    border: 1px solid #404040;
                    padding: 8px 12px;
                    text-align: left;
                }
                th {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    font-weight: 600;
                }
                tr:nth-child(even) {
                    background-color: #262626;
                }
                hr {
                    border: none;
                    border-top: 1px solid #404040;
                    margin: 1.5em 0;
                }
                strong { color: #ffffff; font-weight: 600; }
                em { color: #e0e0e0; font-style: italic; }
            </style>
            """
            html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br'])
            html = css + html
            self.text_display.setHtml(html)
        except Exception as e:
            # Fallback to plain text if markdown conversion fails
            print(f"Markdown渲染失败: {str(e)}")
            self.text_display.setPlainText(text)
        
        # If no position is provided, center on screen
        if position is None:
            # Get the screen geometry
            screen = QApplication.primaryScreen().geometry()
            # Calculate center position
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            position = QPoint(x, y)
        
        # Only move the window if it's not already visible
        if not self.isVisible():
            self.move(position)
            self.show()
            self.raise_()
            
            # Add fade-in animation
            self.setWindowOpacity(0)
            self.fade_in()
    
    def fade_in(self):
        """Fade in animation"""
        self._opacity = 0
        self._fade_timer = QTimer()
        self._fade_timer.timeout.connect(self._update_fade_in)
        self._fade_timer.start(20)
    
    def _update_fade_in(self):
        self._opacity += 0.05
        if self._opacity >= 1:
            self._opacity = 1
            self._fade_timer.stop()
        self.setWindowOpacity(self._opacity)

    def set_mode(self, mode):
        """Set the window mode (summary or translate)"""
        self.current_mode = mode
        if mode == "summary":
            self.title_label.setText("AI 文本总结")
            self.icon_label.setText("📊")
        elif mode == "translate":
            self.title_label.setText("AI 文本翻译")
            self.icon_label.setText("🌐")
        
        # Update icon if using image
        icon_pixmap = QIcon("icon.png").pixmap(QSize(20, 20))
        if not icon_pixmap.isNull():
            self.icon_label.setPixmap(icon_pixmap)

class SettingsDialog(QDialog):
    def __init__(self, api_key="", base_url="", target_language="中文", parent=None):
        super().__init__(parent)
        self.setWindowTitle("API 设置")
        self.setModal(True)
        self.setFixedSize(500, 250)
        
        # Set dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #363636;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #58a6ff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #363636;
            }
        """)
        
        # Create layout
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # API Key input with show/hide button
        api_key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(api_key)
        self.api_key_input.setPlaceholderText("请输入 DeepSeek API 密钥")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_layout.addWidget(self.api_key_input)
        
        # Show/Hide password button
        self.show_password_btn = QPushButton("显示")
        self.show_password_btn.setFixedWidth(60)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        api_key_layout.addWidget(self.show_password_btn)
        
        layout.addRow("API 密钥:", api_key_layout)
        
        # Base URL input
        self.base_url_input = QLineEdit()
        self.base_url_input.setText(base_url)
        self.base_url_input.setPlaceholderText("https://api.deepseek.com/v1")
        layout.addRow("API 地址:", self.base_url_input)
        
        # Target language selection
        from PyQt6.QtWidgets import QComboBox
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "中文", "English", "日本語", "한국어", 
            "Español", "Français", "Deutsch", "Русский",
            "Português", "Italiano", "Nederlands", "Polski"
        ])
        self.language_combo.setCurrentText(target_language)
        layout.addRow("翻译目标语言:", self.language_combo)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
    
    def get_settings(self):
        """Return the current settings"""
        return {
            'api_key': self.api_key_input.text().strip(),
            'base_url': self.base_url_input.text().strip() or 'https://api.deepseek.com/v1',
            'target_language': self.language_combo.currentText()
        }
    
    def toggle_password_visibility(self):
        """Toggle the password visibility"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("显示")

class TextSummaryAssistant(QWidget):
    clipboard_text_ready = pyqtSignal(str)
    clipboard_error = pyqtSignal(str)

    def __init__(self):
        # Configure high DPI settings before creating QApplication
        try:
            from PyQt6.QtCore import Qt
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
        except:
            pass
            
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
            # Prevent app from quitting when last window closes
            self.app.setQuitOnLastWindowClosed(False)
        else:
            self.app = QApplication.instance()
            self.app.setQuitOnLastWindowClosed(False)
            
        super().__init__()
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        self.target_language = os.getenv('TARGET_LANGUAGE', '中文')
        
        if not self.api_key:
            print("错误：未设置 DEEPSEEK_API_KEY 环境变量")
        if not self.base_url:
            print("警告：未设置 DEEPSEEK_BASE_URL 环境变量，使用默认值")
        
        self.floating_window = FloatingWindow()
        self.floating_icon = FloatingIcon()
        self.floating_icon.on_action_callback = self.on_action_selected
        self.setup_tray()
        
        self.last_selected_text = ""
        self.is_processing = False
        self.summarize_thread = None
        self.is_summarizing = False
        self.current_operation = "summary"  # Track current operation type
        
        # Setup selection monitoring
        self.setup_selection_monitoring()
        
        # Connect our own signals
        self.clipboard_text_ready.connect(self._handle_clipboard_text)
        self.clipboard_error.connect(self._handle_clipboard_error)

    def setup_selection_monitoring(self):
        """Setup continuous text selection monitoring"""
        # Use a timer to periodically check for selected text
        self.selection_timer = QTimer(self)
        self.selection_timer.timeout.connect(self.check_for_selection)
        self.selection_timer.start(1000)  # Start with 1 second interval
        
        # Disable automatic deselection checking to prevent icon from disappearing too quickly
        # self.deselection_timer = QTimer(self)
        # self.deselection_timer.timeout.connect(self.check_for_deselection)
        # self.deselection_timer.start(5000)  # Check every 5 seconds (less frequent)
        
        self.last_checked_text = ""
        self.last_mouse_pos = None
        self.mouse_idle_count = 0
        self.last_clipboard_check_time = 0
        self.active_monitoring = False
        self.last_activity_time = time.time()
        print("文本选择监控已启动（智能模式）")

    def check_for_selection(self):
        """Check if there's any selected text"""
        if self.is_processing or self.is_summarizing:
            return
            
        try:
            # Get current mouse position
            cursor_pos = win32gui.GetCursorPos()
            current_time = time.time()
            
            # Check if mouse has moved
            if self.last_mouse_pos is None:
                self.last_mouse_pos = cursor_pos
                return
            
            # Detect mouse movement
            if cursor_pos != self.last_mouse_pos:
                # Mouse moved, enter active monitoring mode
                if not self.active_monitoring:
                    self.active_monitoring = True
                    self.selection_timer.setInterval(300)  # Switch to fast checking
                    print("检测到鼠标活动，进入活跃监控模式")
                
                self.last_activity_time = current_time
                self.mouse_idle_count = 0
                self.last_mouse_pos = cursor_pos
                return
            
            # Mouse hasn't moved
            if self.active_monitoring:
                self.mouse_idle_count += 1
                
                # Check if we should perform selection check
                if self.mouse_idle_count == 2:  # After 600ms of idle
                    # Check for selection
                    if current_time - self.last_clipboard_check_time >= 1.0:
                        self.perform_selection_check(cursor_pos)
                
                # Exit active monitoring after 3 seconds of inactivity
                if current_time - self.last_activity_time > 3.0:
                    self.active_monitoring = False
                    self.selection_timer.setInterval(1000)  # Switch back to slow checking
                    self.mouse_idle_count = 0
                    print("鼠标长时间静止，退出活跃监控模式")
            
        except Exception as e:
            if not isinstance(e, KeyboardInterrupt):
                print(f"检查时出错: {type(e).__name__}: {str(e)}")

    def perform_selection_check(self, cursor_pos):
        """Perform the actual selection check"""
        try:
            self.last_clipboard_check_time = time.time()
            print(f"执行选择检查... (位置: {cursor_pos})")
            
            # Save current clipboard
            old_clipboard = self.get_clipboard_safely()
            
            # Use pyautogui to simulate Ctrl+C
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.1)
            
            # Get new clipboard content
            new_clipboard = self.get_clipboard_safely()
            
            # Debug output
            if old_clipboard != new_clipboard:
                print(f"剪贴板内容变化: 旧内容长度={len(old_clipboard) if old_clipboard else 0}, 新内容长度={len(new_clipboard) if new_clipboard else 0}")
            
            # Check if we got new text
            if (new_clipboard and 
                new_clipboard != old_clipboard and 
                new_clipboard != self.last_checked_text and
                len(new_clipboard.strip()) > 0):
                
                print(f"检测到选中文本: {len(new_clipboard)} 字符")
                print(f"文本预览: {new_clipboard[:50]}..." if len(new_clipboard) > 50 else f"文本: {new_clipboard}")
                
                self.last_checked_text = new_clipboard
                self.last_selected_text = new_clipboard
                self.floating_icon.selected_text = new_clipboard
                
                # Show icon near cursor
                screen_rect = win32api.GetMonitorInfo(
                    win32api.MonitorFromPoint(cursor_pos)
                )['Work']
                
                x = min(cursor_pos[0] + 20, screen_rect[2] - 40)
                y = min(cursor_pos[1] - 40, screen_rect[3] - 40)
                
                print(f"准备显示图标在位置: ({x}, {y})")
                self.floating_icon.move(x, y)
                self.floating_icon.show()
                self.floating_icon.raise_()
                self.floating_icon.activateWindow()
                # Record the time when icon is shown
                self.icon_show_time = time.time()
                print("图标已显示")
                
                # Reset monitoring state
                self.mouse_idle_count = 0
                self.active_monitoring = False
                self.selection_timer.setInterval(1000)  # Back to slow mode
                
                # Restore old clipboard if needed
                if old_clipboard and old_clipboard != new_clipboard:
                    self.restore_clipboard(old_clipboard)
            else:
                # Check if text selection was cleared
                if (self.floating_icon.isVisible() and 
                    new_clipboard == old_clipboard and 
                    self.last_checked_text and
                    new_clipboard != self.last_checked_text):
                    
                    print("检测到文本选择被取消，隐藏图标")
                    self.floating_icon.hide()
                    self.last_checked_text = ""
                    self.last_selected_text = ""
                    
                elif new_clipboard == self.last_checked_text and new_clipboard:
                    print("检测到相同的文本，跳过")
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            if not isinstance(e, KeyboardInterrupt):
                print(f"选择检查时出错: {str(e)}")

    def get_clipboard_safely(self):
        """Safely get clipboard content"""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return text
            return ""
        except:
            return ""
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

    def restore_clipboard(self, text):
        """Restore clipboard content"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        except:
            pass
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

    def __del__(self):
        """Cleanup when the application closes"""
        try:
            if hasattr(self, 'selection_timer'):
                self.selection_timer.stop()
                print("选择监控已停止")
            # Deselection timer is disabled
            # if hasattr(self, 'deselection_timer'):
            #     self.deselection_timer.stop()
            #     print("取消选择监控已停止")
        except Exception as e:
            print(f"清理时出错: {str(e)}")
        super().__del__() if hasattr(super(), '__del__') else None

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("icon.png"))
        
        # Create tray menu with custom styling
        tray_menu = QMenu()
        
        # Add custom stylesheet to make menu more compact
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                padding: 2px;
            }
            QMenu::item {
                padding: 4px 20px 4px 20px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #404040;
                border-radius: 2px;
            }
            QMenu::separator {
                height: 1px;
                background: #3a3a3a;
                margin: 4px 10px;
            }
        """)
        
        # Add menu items
        settings_action = QAction("设置", self.app)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        about_action = QAction("关于", self.app)
        about_action.triggered.connect(self.show_about)
        tray_menu.addAction(about_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Show tooltip with instructions
        self.tray_icon.setToolTip("文本总结助手\n选中文本后点击图标即可触发总结\n右键点击图标可隐藏")

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.api_key, self.base_url, self.target_language)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            
            self.api_key = settings['api_key']
            self.base_url = settings['base_url']
            self.target_language = settings['target_language']
            
            # Save settings to .env file
            self.save_settings()
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "设置已保存",
                "API 设置已成功保存！"
            )
    
    def save_settings(self):
        """Save settings to .env file"""
        try:
            env_content = f"""# DeepSeek API Configuration
DEEPSEEK_API_KEY={self.api_key}
DEEPSEEK_BASE_URL={self.base_url}
TARGET_LANGUAGE={self.target_language}
"""
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("设置已保存到 .env 文件")
        except Exception as e:
            print(f"保存设置失败: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox
        # Create a message box with the main widget as parent
        msg_box = QMessageBox()
        msg_box.setWindowTitle("关于文本总结助手")
        msg_box.setText("文本总结助手 v1.0")
        msg_box.setInformativeText(
            "使用方法:\n"
            "1. 选中任意文本\n"
            "2. 等待图标出现\n"
            "3. 左键点击图标选择操作\n"
            "4. 右键点击图标可隐藏\n\n"
            "Powered by DeepSeek API"
        )
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()

    def _handle_clipboard_text(self, text):
        """Handle clipboard text in the main thread"""
        print("在主线程中处理剪贴板文本")
        self.is_processing = False
        
        if text and text.strip() and text != self.last_selected_text:
            print(f"发现新文本，长度: {len(text)}")
            self.last_selected_text = text
            self.floating_icon.selected_text = text
            
            try:
                # Position the icon near the last mouse position
                if hasattr(self, 'last_mouse_pos'):
                    screen_rect = QGuiApplication.primaryScreen().geometry()
                    x = min(self.last_mouse_pos.x() + 20, screen_rect.width() - 40)
                    y = min(self.last_mouse_pos.y() - 40, screen_rect.height() - 40)
                    print(f"图标将显示在位置: ({x}, {y})")
                    
                    # Show the icon in the next event loop iteration
                    QTimer.singleShot(0, lambda: self._show_icon(x, y))
                    print("已安排显示图标")
            except Exception as e:
                print(f"显示图标时出错: {str(e)}")
        else:
            print("没有新的文本或文本未变化")
            self.floating_icon.hide()
            if not text or not text.strip():
                self.last_selected_text = ""

    def _show_icon(self, x, y):
        """Helper method to show the icon"""
        try:
            self.floating_icon.move(x, y)
            self.floating_icon.show()
            self.floating_icon.raise_()
            # Record the time when icon is shown
            self.icon_show_time = time.time()
            print("图标已显示")
        except Exception as e:
            print(f"显示图标失败: {str(e)}")

    @pyqtSlot(str)
    def _handle_clipboard_error(self, error_msg):
        """Handle clipboard error in the main thread"""
        print("在主线程中处理剪贴板错误")
        self.is_processing = False
        print(f"获取剪贴板文本出错: {error_msg}")
        self.floating_icon.hide()
        self.last_selected_text = ""

    def on_clipboard_text_ready(self, text):
        """Deprecated: Use _handle_clipboard_text instead"""
        print("警告：使用了已废弃的方法 on_clipboard_text_ready")
        self._handle_clipboard_text(text)

    def on_clipboard_error(self, error_msg):
        """Deprecated: Use _handle_clipboard_error instead"""
        print("警告：使用了已废弃的方法 on_clipboard_error")
        self._handle_clipboard_error(error_msg)

    def summarize_text(self, text):
        if self.is_summarizing:
            print("已经在进行总结，请等待当前总结完成")
            return "正在处理另一个总结请求，请稍后再试..."

        if not self.api_key:
            return "错误：未设置 DeepSeek API 密钥"

        print("开始调用API进行总结")
        self.is_summarizing = True
        
        # Create and start the summarize thread
        if self.summarize_thread and self.summarize_thread.isRunning():
            print("等待之前的总结线程完成")
            self.summarize_thread.wait()
        
        self.summarize_thread = SummarizeThread(text, self.api_key, self.base_url)
        self.summarize_thread.finished.connect(self.on_summary_finished)
        self.summarize_thread.error.connect(self.on_summary_error)
        self.summarize_thread.chunk_received.connect(self.on_chunk_received)  # Connect the new signal
        self.summarize_thread.start()
        
        return "正在生成总结，请稍候..."

    def on_chunk_received(self, chunk):
        """Handle streaming chunks of the summary"""
        self.floating_window.update_summary(chunk)

    def on_summary_finished(self, result):
        print("API调用成功")
        self.is_summarizing = False
        # Final update with complete summary/translation using current operation mode
        self.floating_window.show_summary(result, mode=self.current_operation)
        self.floating_icon.hide()

    def on_summary_error(self, error_msg):
        print(f"API调用失败: {error_msg}")
        self.is_summarizing = False
        # Show error in the center of the screen using current operation mode
        operation_name = "总结" if self.current_operation == "summary" else "翻译"
        self.floating_window.show_summary(f"{operation_name}出错：{error_msg}", mode=self.current_operation)
        self.floating_icon.hide()

    def on_action_selected(self, text, action):
        # Hide the floating icon immediately when user selects an action
        self.floating_icon.hide()
        
        if action == "summary":
            self.current_operation = "summary"
            summary = self.summarize_text(text)
            self.floating_window.show_summary(summary, mode="summary")
        elif action == "translate":
            self.current_operation = "translate"
            translation = self.translate_text(text)
            self.floating_window.show_summary(translation, mode="translate")

    def translate_text(self, text):
        if self.is_summarizing:
            print("已经在进行处理，请等待当前任务完成")
            return "正在处理另一个请求，请稍后再试..."

        if not self.api_key:
            return "错误：未设置 DeepSeek API 密钥"

        print(f"开始调用API进行翻译到{self.target_language}")
        self.is_summarizing = True  # 使用同一个标志位防止并发
        
        # Create and start the translate thread
        if self.summarize_thread and self.summarize_thread.isRunning():
            print("等待之前的处理线程完成")
            self.summarize_thread.wait()
        
        self.summarize_thread = TranslateThread(text, self.api_key, self.base_url, self.target_language)
        self.summarize_thread.finished.connect(self.on_summary_finished)  # 复用相同的处理函数
        self.summarize_thread.error.connect(self.on_summary_error)
        self.summarize_thread.chunk_received.connect(self.on_chunk_received)
        self.summarize_thread.start()
        
        return f"正在翻译到{self.target_language}，请稍候..."



    def check_for_deselection(self):
        """Check if text selection has been cleared and hide icon if needed"""
        # This method is currently disabled to prevent premature icon hiding
        # The icon will only be hidden when user clicks on it or manually
        return

    def run(self):
        print("程序启动，开始运行事件循环")
        sys.exit(self.app.exec())

if __name__ == '__main__':
    try:
        print("初始化应用程序...")
        assistant = TextSummaryAssistant()
        print("应用程序初始化完成，开始运行")
        assistant.run()
    except Exception as e:
        print(f"程序出错: {str(e)}")
        sys.exit(1)
