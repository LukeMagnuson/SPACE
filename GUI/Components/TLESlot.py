from PyQt5.QtWidgets import QApplication, QFrame,QPushButton, QCheckBox, QWidget, QLabel, QHBoxLayout, QVBoxLayout,  QGraphicsOpacityEffect
from PyQt5.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, Qt

class TLESlot(QWidget):
    def __init__(self, tle_display, name, line_1, line_2):
        super().__init__()

        self.enabled = True
        self.delete_me = False
        self.expanded = False  # collapsed by default

        self.tle_display = tle_display
        self.tle_name = name
        self.tle_line_1 = line_1
        self.tle_line_2 = line_2

        # Outer vertical layout
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(2)

        # --- Top bar ---
        self.top_bar = QHBoxLayout()
        self.top_bar.setContentsMargins(0, 0, 0, 0)
        self.top_bar.setSpacing(5)

        # Checkbox
        self.checkbox = QCheckBox("")
        self.checkbox.setToolTip("Enable" if self.enabled else "Disable")
        self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self.checkbox_changed)
        self.top_bar.addWidget(self.checkbox)

        # Label
        self.label = QLabel(self.tle_name)
        self.top_bar.addWidget(self.label)

        # Toggle button
        self.toggle_button = QPushButton("▼")
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.clicked.connect(self.toggle_expand)
        self.top_bar.addWidget(self.toggle_button)

        # Delete button
        self.delete_button = QPushButton("🗑")
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.clicked.connect(self.delete)
        self.top_bar.addWidget(self.delete_button)

        self.outer_layout.addLayout(self.top_bar)

        # --- Expandable area ---
        self.expand_area = QFrame()
        self.expand_area.setFixedHeight(0)  # collapsed initially
        self.expand_area.setMaximumHeight(0)  # force collapsed
        self.expand_area.setStyleSheet("background-color: #dcdcdc; border: 1px solid #444;")

        expand_layout = QVBoxLayout(self.expand_area)
        expand_layout.setContentsMargins(5, 5, 5, 5)

        self.tle_text = QLabel(f"{self.tle_line_1}\n{self.tle_line_2}")
        self.tle_text.setWordWrap(True)
        expand_layout.addWidget(self.tle_text)

        self.outer_layout.addWidget(self.expand_area)

        # Animation for smooth expand/collapse
        self.anim = QPropertyAnimation(self.expand_area, b"maximumHeight")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        QApplication.instance().installEventFilter(self)

    def checkbox_changed(self, state):
        self.enabled = (state == Qt.Checked)
        self.checkbox.setToolTip("Enable" if self.enabled else "Disable")

    def delete(self):
        if not self.delete_me:
            self.delete_me = True
            self.delete_button.setStyleSheet("background-color: red;")
        else:
            self.tle_display.delete_element(self.tle_name)

    def toggle_expand(self):
        self.expanded = not self.expanded
        self.toggle_button.setText("▲" if self.expanded else "▼")

        start_height = self.expand_area.maximumHeight()
        end_height = 150 if self.expanded else 0

        self.anim.stop()
        self.anim.setStartValue(start_height)
        self.anim.setEndValue(end_height)
        self.anim.start()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            if not self.delete_button.geometry().contains(event.pos()):
                if self.delete_me:
                    self.delete()
                else:
                    self.delete_me = False
                    self.delete_button.setStyleSheet("")
        return super().eventFilter(obj, event)