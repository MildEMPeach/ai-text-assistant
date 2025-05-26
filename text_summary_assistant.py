import sys
import os
import win32clipboard
import win32con
import win32gui
import win32api
import requests
import keyboard
import time
import markdown
from dotenv import load_dotenv
from openai import OpenAI
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                           QWidget, QTextBrowser, QPushButton, QVBoxLayout, QLabel)
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
            self.hide()
            if hasattr(self, 'on_click_callback'):
                self.on_click_callback(self.selected_text)

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()
        self.current_summary = ""

    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create container widget with background
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)
        
        # Create title label
        title_label = QLabel("文本总结")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        container_layout.addWidget(title_label)
        
        # Create text display area using QTextBrowser instead of QTextEdit
        self.text_display = QTextBrowser()
        self.text_display.setOpenExternalLinks(True)  # Allow clicking links
        self.text_display.setStyleSheet("""
            QTextBrowser {
                background-color: #363636;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #404040;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        container_layout.addWidget(self.text_display)
        
        # Create button container for better alignment
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create close button
        close_button = QPushButton("关闭")
        close_button.setFixedWidth(100)  # Set fixed width for button
        close_button.clicked.connect(self.hide)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d13438;
            }
            QPushButton:pressed {
                background-color: #b22222;
            }
        """)
        button_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        button_container.setLayout(button_layout)
        container_layout.addWidget(button_container)
        
        # Set container layout
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Set initial size
        self.resize(400, 300)

    def update_summary(self, text):
        """Update the summary text with streaming content"""
        self.current_summary = text
        self.show_summary(text, self.pos())

    def show_summary(self, text, position=None):
        # Convert Markdown to HTML
        try:
            # Add custom CSS for dark theme
            css = """
            <style>
                body { color: #ffffff; }
                a { color: #58a6ff; }
                code { 
                    background-color: #2f2f2f; 
                    padding: 2px 4px;
                    border-radius: 3px;
                }
                pre {
                    background-color: #2f2f2f;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
                blockquote {
                    border-left: 4px solid #404040;
                    margin: 0;
                    padding-left: 10px;
                    color: #a0a0a0;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #404040;
                    padding: 6px;
                }
                th {
                    background-color: #2f2f2f;
                }
            </style>
            """
            html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
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

class TextSummaryAssistant(QWidget):
    # Define signals at class level
    clipboard_text_ready = pyqtSignal(str)
    clipboard_error = pyqtSignal(str)

    def __init__(self):
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        super().__init__()
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        
        if not self.api_key:
            print("错误：未设置 DEEPSEEK_API_KEY 环境变量")
        if not self.base_url:
            print("警告：未设置 DEEPSEEK_BASE_URL 环境变量，使用默认值")
        
        self.floating_window = FloatingWindow()
        self.floating_icon = FloatingIcon()
        self.floating_icon.on_click_callback = self.on_icon_click
        self.setup_tray()
        self.setup_keyboard()
        self.last_selected_text = ""
        self.is_processing = False
        self.last_hotkey_time = 0
        self.summarize_thread = None
        self.clipboard_thread = None
        self.is_summarizing = False
        
        # Connect our own signals
        self.clipboard_text_ready.connect(self._handle_clipboard_text)
        self.clipboard_error.connect(self._handle_clipboard_error)
        
        # Setup a timer to process events
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_events)
        self.timer.start(100)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("icon.png"))
        
        # Create tray menu
        tray_menu = QMenu()
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Show tooltip with instructions
        self.tray_icon.setToolTip("选中文本后按 Ctrl+Q 触发总结")

    def setup_keyboard(self):
        keyboard.on_press(self.on_key_event)

    def on_key_event(self, e):
        # Check if it's our hotkey combination (Ctrl+Q)
        current_time = time.time()
        if (e.name == 'q' and keyboard.is_pressed('ctrl') and 
            not self.is_processing and 
            not self.is_summarizing and
            current_time - self.last_hotkey_time > 0.5):
            print("快捷键触发")
            self.last_hotkey_time = current_time
            self.check_selected_text()

    def process_events(self):
        """Process events and check thread status"""
        try:
            self.app.processEvents()
            
            # Check if clipboard thread is done but signal wasn't received
            if self.clipboard_thread and not self.clipboard_thread.isRunning():
                print("检测到剪贴板线程已完成")
                if self.is_processing:
                    print("重置处理状态")
                    self.is_processing = False
                self.clipboard_thread.deleteLater()
                self.clipboard_thread = None
        except Exception as e:
            print(f"处理事件时出错: {str(e)}")

    def check_selected_text(self):
        if self.is_summarizing:
            print("正在进行总结，请等待完成")
            return

        if self.clipboard_thread and self.clipboard_thread.isRunning():
            print("正在获取剪贴板内容，请稍候")
            return

        print("开始检查选中文本")
        self.is_processing = True
        
        # Clean up old thread if exists
        if self.clipboard_thread:
            self.clipboard_thread.deleteLater()
        
        # Create new thread
        self.clipboard_thread = ClipboardThread()
        
        # Connect signals directly to handler methods
        print("连接信号处理函数")
        self.clipboard_thread.text_ready.connect(self._handle_clipboard_text)
        self.clipboard_thread.error.connect(self._handle_clipboard_error)
        
        # Start thread
        self.clipboard_thread.start()
        print("剪贴板线程已启动")

    @pyqtSlot(str)
    def _handle_clipboard_text(self, text):
        """Handle clipboard text in the main thread"""
        print("在主线程中处理剪贴板文本")
        self.is_processing = False
        if text and text != self.last_selected_text:
            print(f"发现新文本，长度: {len(text)}")
            self.last_selected_text = text
            self.floating_icon.selected_text = text
            
            try:
                # Get cursor position
                cursor_pos = win32gui.GetCursorPos()
                print(f"当前鼠标位置: {cursor_pos}")
                screen_rect = win32api.GetMonitorInfo(
                    win32api.MonitorFromPoint(cursor_pos)
                )['Work']
                print(f"屏幕工作区: {screen_rect}")
                
                # Position the icon near the cursor
                x = min(cursor_pos[0] + 20, screen_rect[2] - 40)
                y = min(cursor_pos[1] - 40, screen_rect[3] - 40)
                print(f"图标将显示在位置: ({x}, {y})")
                
                # Move and show the icon in the next event loop iteration
                QTimer.singleShot(0, lambda: self._show_icon(x, y))
                print("已安排显示图标")
            except Exception as e:
                print(f"显示图标时出错: {str(e)}")
        else:
            print("没有新的文本或文本未变化")
            self.floating_icon.hide()
            self.last_selected_text = ""

    def _show_icon(self, x, y):
        """Helper method to show the icon"""
        try:
            self.floating_icon.move(x, y)
            self.floating_icon.show()
            self.floating_icon.raise_()
            self.floating_icon.repaint()
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
        # Final update with complete summary
        self.floating_window.show_summary(result)
        self.floating_icon.hide()

    def on_summary_error(self, error_msg):
        print(f"API调用失败: {error_msg}")
        self.is_summarizing = False
        # Show error in the center of the screen
        self.floating_window.show_summary(f"总结出错：{error_msg}")
        self.floating_icon.hide()

    def on_icon_click(self, text):
        if not text or self.is_summarizing:
            return
            
        print(f"点击图标，文本长度: {len(text)}")
        summary = self.summarize_text(text)
        # Show initial message in the center of the screen
        self.floating_window.show_summary(summary)

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