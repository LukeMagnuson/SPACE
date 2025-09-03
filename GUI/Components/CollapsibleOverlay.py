from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation
from PyQt5.QtWidgets import QPushButton, QWidget, QFrame, QHBoxLayout, QPushButton, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect
from enum import Enum

class OverlaySide(Enum):
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4

class CollapsibleOverlay(QFrame):
    def __init__(self, parent=None, side = OverlaySide.LEFT):
        super().__init__(parent)

        self.side = side
        self.expanded = False

        self.full_width = 300   # Expanded width
        self.collapsed_width = 20
        self.above_height_amount = 0
        self.control_panel_height_reduction = 110

        # Layout: button on left, overlay content on right
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toggle button
        self.toggle_button = QPushButton("▲\nC\no\nl\nl\na\np\ns\ne")
        self.toggle_button.setFixedWidth(self.collapsed_width)
        self.toggle_button.clicked.connect(self.toggle_width)
        self.main_layout.addWidget(self.toggle_button)

        # Overlay content container
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: #dddddd;")

        self.content_layout = QVBoxLayout(self.overlay)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Fade effect for overlay contents
        self.opacity_effect = QGraphicsOpacityEffect(self.overlay)
        self.overlay.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        self.main_layout.addWidget(self.overlay, stretch=1)

        self.update_size()

    def toggle_width(self):
        self.expanded = not self.expanded
        self.toggle_button.setText(
            "▲\nC\no\nl\nl\na\np\ns\ne" if self.expanded else "▼\nE\nx\np\na\nn\nd"
        )

        self.animate_size()
        self.animate_fade()

    def update_size(self):
        target_width = self.full_width if self.expanded else self.collapsed_width
        target_height = (
            self.parent().height()
            - self.above_height_amount
            - self.control_panel_height_reduction
        )
        self.setFixedSize(target_width, target_height)
        self.toggle_button.setFixedHeight(target_height)

    def animate_size(self):
        start_width = self.width()
        end_width = self.full_width if self.expanded else self.collapsed_width
        target_height = (
            self.parent().height()
            - self.above_height_amount
            - self.control_panel_height_reduction
        )

        # Lock height first
        self.setFixedHeight(target_height)
        self.toggle_button.setFixedHeight(target_height)

        # Animate width smoothly
        animation = QPropertyAnimation(self, b"minimumWidth")
        animation.setDuration(300)
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        animation.start()
        self._animation = animation  # keep reference

    def animate_fade(self):
        # Fade out when collapsing, fade in when expanding
        end_opacity = 1.0 if self.expanded else 0.0
        fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade.setDuration(300)
        fade.setStartValue(self.opacity_effect.opacity())
        fade.setEndValue(end_opacity)
        fade.setEasingCurve(QEasingCurve.InOutCubic)
        fade.start()
        self._fade = fade