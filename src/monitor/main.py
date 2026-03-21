# monitor/main.py
# Cross-platform Qt Application Window
#
# @author n1ghts4kura
# @date 2026-03-20
#

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLineEdit, QPushButton, QSizePolicy, QLabel,
    QScrollBar, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QFont, QFontMetrics


class CircularIconButton(QPushButton):
    def __init__(self, icon_text: str, tooltip: str = "", parent=None):
        super().__init__(icon_text, parent)
        self.setFixedSize(44, 44)
        self.setToolTip(tooltip)
        self.setCheckable(True)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 22px;
                background-color: #F0F0F0;
                color: #888888;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                color: #555555;
            }
            QPushButton:checked {
                background-color: #2563EB;
                color: white;
            }
        """)

    def sizeHint(self) -> QSize:
        return QSize(44, 44)


class MessageBubble(QWidget):
    """Message bubble that always fills available horizontal width."""

    avatar_size = 36
    spacing = 10
    padding_h = 16
    padding_v = 10
    radius = 16

    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self._text = text
        self._label = None
        self._avatar = None
        self._setup_ui(text)

    def _setup_ui(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.spacing)

        # Avatar
        avatar_btn = QPushButton("R" if not self.is_user else "U")
        avatar_btn.setFixedSize(self.avatar_size, self.avatar_size)
        color = "#2563EB" if not self.is_user else "#10B981"
        avatar_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: {self.avatar_size // 2}px;
                background-color: {color};
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        avatar_btn.setEnabled(False)
        self._avatar = avatar_btn

        # Bubble container
        bubble = QWidget()
        bubble.setStyleSheet(f"""
            background-color: #F1F5F9;
            border-radius: {self.radius}px;
        """ if not self.is_user else f"""
            background-color: #2563EB;
            border-radius: {self.radius}px;
        """)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(
            self.padding_h, self.padding_v, self.padding_h, self.padding_v
        )
        bubble_layout.setSpacing(0)

        # Text label - NO word wrap on the label itself
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        label.setStyleSheet("border: none; background: transparent;")
        self._label = label
        bubble_layout.addWidget(label)

        if self.is_user:
            layout.addWidget(label, 1)
            layout.addWidget(avatar_btn, 0, Qt.AlignmentFlag.AlignTop)
        else:
            layout.addWidget(avatar_btn, 0, Qt.AlignmentFlag.AlignTop)
            layout.addWidget(label, 1)

    def sizeHint(self) -> QSize:
        # Return full available width hint
        parent_width = self.parent().width() if self.parent() else 400
        return QSize(parent_width, 60)


class AutoExpandTextEdit(QTextEdit):
    """
    A auto-expanding text input.
    - Shows single-line height when empty
    - Visually wraps text but keeps it as one logical line (Shift+Enter for real newlines)
    - Auto-expands vertically as content grows
    """

    def __init__(self, placeholder: str = "", max_height: int = 120, parent=None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._max_height = max_height
        self.setPlaceholderText(placeholder)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.document().setDocumentMargin(0)
        self.textChanged.connect(self._update_height)
        self._update_height()

    def _calc_height(self) -> int:
        """Calculate required height based on actual text wrapping."""
        fm = self.fontMetrics()
        available_w = max(self.width(), 100)
        padding = 8

        text = self.toPlainText()
        if not text:
            return fm.height() + padding * 2

        # Count visual lines by simulating word-wrap
        words = text.split('\n')
        total_lines = 0
        for para in words:
            if not para:
                total_lines += 1
                continue
            # Wrap words manually using horizontalAdvance
            line_width = 0
            for word in para.split():
                word_w = fm.horizontalAdvance(word)
                space_w = fm.horizontalAdvance(' ')
                if line_width == 0:
                    line_width = word_w
                elif line_width + space_w + word_w <= available_w:
                    line_width += space_w + word_w
                else:
                    total_lines += 1
                    line_width = word_w
            if line_width > 0:
                total_lines += 1

        return total_lines * fm.lineSpacing() + padding * 2

    def _update_height(self):
        h = self._calc_height()
        self.setMinimumHeight(h)
        self.setMaximumHeight(self._max_height)
        self.updateGeometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_height()


class ChatMonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SenseReAct Monitor")
        self.setFixedSize(500, 780)
        self.setStyleSheet("background-color: white;")
        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(80)
        sidebar.setStyleSheet("background-color: #FAFAFA;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(20)

        icons = [("C", "Chat"), ("S", "Simulator"), ("L", "Logs"), ("G", "Settings")]
        for text, tooltip in icons:
            btn = CircularIconButton(text, tooltip)
            if text == "C":
                btn.setChecked(True)
            sidebar_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)

        sidebar_layout.addStretch()

        # Right Chat Panel
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(16, 16, 24, 16)
        chat_layout.setSpacing(12)

        # Chat history (~90%)
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: white; }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 4px 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #E0E0E0;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background-color: #CCCCCC; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        history_content = QWidget()
        history_layout = QVBoxLayout(history_content)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(16)
        history_layout.addStretch()

        default_messages = [
            ("你好，我是红方机器人控制助手。有什么可以帮助你的吗？", False),
            ("请帮我移动到指定位置。", True),
            ("好的，正在规划路径并移动到目标位置。", False),
        ]

        for text, is_user in default_messages:
            bubble = MessageBubble(text, is_user)
            history_layout.insertWidget(history_layout.count() - 1, bubble)

        chat_scroll.setWidget(history_content)

        # Input area - outer container provides background + border
        input_container = QWidget()
        input_container.setStyleSheet("""
            background-color: #F8FAFC;
            border-radius: 20px;
            border: 1px solid #E2E8F0;
        """)
        outer_layout = QVBoxLayout(input_container)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Inner widget where content is centered (like CSS flex justify/align-center)
        input_inner = QWidget()
        inner_layout = QHBoxLayout(input_inner)
        inner_layout.setContentsMargins(12, 8, 8, 8)
        inner_layout.setSpacing(8)

        input_box = AutoExpandTextEdit(placeholder="输入消息...", max_height=96)
        input_box.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
                color: #1E293B;
                font-family: 'Microsoft YaHei';
                padding: 8px 12px;
            }
            QTextEdit::placeholder { color: #94A3B8; }
        """)

        send_btn = QPushButton("↑")
        send_btn.setFixedSize(36, 36)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)

        inner_layout.addWidget(input_box, 1, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(send_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        outer_layout.addWidget(input_inner)

        chat_layout.addWidget(chat_scroll, 1)
        chat_layout.addWidget(input_container, 0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(chat_panel, 1)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    window = ChatMonitorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
