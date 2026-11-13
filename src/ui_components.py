# -*- coding: utf-8 -*-
"""
UI component helpers: theming, widget factories, and layout builders.
"""

from PyQt5.QtGui import QFont, QBrush, QColor, QIcon, QCursor
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QSize

from config import (
    FONTS, THEMES, ICON_PATH, ARDUINO_ICON, SAVE_ICON, INFO_ICON,
    INPUT_MASKS, MACRO_TABLE_COLUMNS, SCREEN_RATIOS
)


# ---------------------------------------------------------------------------
# Theme manager
# ---------------------------------------------------------------------------
class ThemeManager:
    """Manages application theme state and provides theme colors."""

    def __init__(self, hmi):
        self.hmi = hmi
        self.current_theme_name = "Bright"

    @property
    def current_theme(self):
        return THEMES[self.current_theme_name]

    def toggle_theme(self):
        """Toggle between 'Bright' and 'Dark' themes."""
        if self.current_theme_name == "Dark":
            self.current_theme_name = "Bright"
        else:
            self.current_theme_name = "Dark"
        return self.current_theme

    def get_font(self, font_key):
        """Return a QFont for the given font key."""
        name, size, bold = FONTS[font_key]
        font = QFont(name, size)
        font.setBold(bold)
        return font

    @staticmethod
    def _make_stylesheet(bg_color):
        """Create a borderless button stylesheet."""
        return f"background-color: {bg_color}; border: none; outline: none;"


# ---------------------------------------------------------------------------
# Widget factory functions
# ---------------------------------------------------------------------------

def create_button(text="", icon_path=None, font_key="base", fixed_width=None, fixed_size=None):
    """Create a styled QPushButton.

    Parameters
    ----------
    text : str
        Button label text.
    icon_path : str or None
        Path to an icon file.
    font_key : str
        Key into the FONTS config dict.
    fixed_width : int or None
        Fixed width in pixels.
    fixed_size : QSize or None
        Fixed width and height.

    Returns
    -------
    QPushButton
    """
    btn = QPushButton(text)
    if font_key:
        btn.setFont(FONTS[font_key])
    if fixed_width is not None:
        btn.setFixedWidth(fixed_width)
    if fixed_size is not None:
        btn.setFixedSize(fixed_size)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    if icon_path:
        btn.setIcon(QIcon(icon_path))
    return btn


def create_label(text="", font_key="section", alignment=Qt.AlignCenter):
    """Create a styled QLabel.

    Parameters
    ----------
    text : str
        Label text.
    font_key : str
        Key into the FONTS config dict.
    alignment : Qt.AlignmentFlag
        Text alignment.

    Returns
    -------
    QLabel
    """
    label = QLabel(text)
    label.setAlignment(alignment)
    if font_key:
        label.setFont(FONTS[font_key])
    return label


def create_textbox(text="", font_key="medium", input_mask=None, alignment=Qt.AlignRight):
    """Create a styled QLineEdit.

    Parameters
    ----------
    text : str
        Initial text.
    font_key : str
        Key into the FONTS config dict.
    input_mask : str or None
        Input mask string.
    alignment : Qt.AlignmentFlag
        Text alignment.

    Returns
    -------
    QLineEdit
    """
    textbox = QLineEdit(text)
    if font_key:
        textbox.setFont(FONTS[font_key])
    if input_mask:
        textbox.setInputMask(input_mask)
    textbox.setAlignment(alignment)
    return textbox


def create_precision_radios(precision_values, hmi):
    """Create radio buttons for precision selection.

    Parameters
    ----------
    precision_values : list of str
        Precision option labels (e.g. ["1", "1/2", ...]).
    hmi
        Reference to the HMI main widget (for the callback).

    Returns
    -------
    tuple
        (list of QRadioButton, QButtonGroup)
    """
    radios = []
    group = QButtonGroup()
    for value in precision_values:
        radio = QRadioButton(value)
        radio.toggled.connect(lambda checked, v=value: _on_precision_changed(hmi, v))
        group.addButton(radio)
        radios.append(radio)
    return radios, group


def _on_precision_changed(hmi, precision):
    """Callback for precision radio button changes."""
    if not hmi.abort_thread:
        hmi.abort_thread = False
    hmi.precision = precision
    hmi.precision_acceleration = 0.1
    hmi.precision_velocity = 0.1
    hmi.precision_position = 0.1
    hmi.db_manager.update_cache_precision(precision)


# ---------------------------------------------------------------------------
# Layout builder helpers
# ---------------------------------------------------------------------------

def build_control_row(hmi, param_key, label_text, textbox, increment_btn, decrement_btn,
                      max_btn, med_btn, min_btn, layout, spacer_height=None):
    """Build a complete control row (label + textbox + three buttons).

    Parameters
    ----------
    hmi
        Reference to the HMI main widget.
    param_key : str
        Parameter key (e.g. 'acceleration').
    label_text : str
        Label text for the row.
    textbox : QLineEdit
        The text input for this parameter.
    increment_btn, decrement_btn : QPushButton
        +/- buttons.
    max_btn, med_btn, min_btn : QPushButton
        Max/Med/Min buttons.
    layout : QVBoxLayout
        Layout to add the row to.
    spacer_height : int or None
        Optional spacer height.
    """
    if spacer_height is not None:
        spacer = QLabel("")
        spacer.setFixedHeight(spacer_height)
        layout.addWidget(spacer)

    layout.addWidget(create_label(label_text, "xlarge"))

    col1_layout = QVBoxLayout()
    col2_layout = QVBoxLayout()
    col3_layout = QVBoxLayout()

    col1_layout.addWidget(textbox)
    col2_layout.addWidget(increment_btn)
    col2_layout.addWidget(decrement_btn)
    col3_layout.addWidget(max_btn)
    col3_layout.addWidget(med_btn)
    col3_layout.addWidget(min_btn)

    row_layout = QHBoxLayout()
    row_layout.addLayout(col1_layout)
    row_layout.addLayout(col2_layout)
    row_layout.addLayout(col3_layout)

    layout.addLayout(row_layout)


def setup_macro_table(table, data, screen_width_ratio=2 / 7):
    """Populate a macro table widget with data.

    Parameters
    ----------
    table : QTableWidget
        The table to populate.
    data : list of tuples
        Macro command data.
    screen_width_ratio : float
        Ratio of screen width to use for table width.
    """
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(MACRO_TABLE_COLUMNS)
    table.setRowCount(len(data))
    table.setShowGrid(False)
    table.verticalHeader().hide()
    table.setFont(FONTS["base"])
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    for i, item in enumerate(data):
        for j in range(len(item)):
            text = str(item[j])
            it = QTableWidgetItem(text)
            if j != 4:
                it.setFlags(Qt.ItemIsSelectable)
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
            it.setTextAlignment(Qt.AlignCenter)
            it.setForeground(QBrush(QColor("black")))
            table.setItem(i, j, it)

    table.adjustSize()
    col_width = int(table.frameGeometry().width() * screen_width_ratio / 5)
    for i in range(5):
        table.setColumnWidth(i, col_width)


def setup_history_table(table, data, screen_width):
    """Populate the command history table.

    Parameters
    ----------
    table : QTableWidget
        The table to populate.
    data : list of tuples
        Command history data (acceleration, velocity, position, inclination).
    screen_width : int
        Screen width in pixels.
    """
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
    table.setFixedWidth(int(screen_width * SCREEN_RATIOS["history_table_width"]))
    table.setShowGrid(False)
    table.verticalHeader().hide()
    table.horizontalHeader().hide()
    table.setFont(FONTS["base"])
    table.setColumnCount(1)
    table.setRowCount(len(data))

    for i, item in enumerate(data):
        text = (
            f"h={item[0]}mm | "
            f"v={item[1]}mm/s | "
            f"a={item[2]}mm/s² | "
            f"\u03b1={item[3]}°"
        )
        it = QTableWidgetItem(text)
        it.setFlags(Qt.ItemIsSelectable)
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        it.setTextAlignment(Qt.AlignCenter)
        it.setForeground(QBrush(QColor("black")))
        table.setItem(i, 0, it)

    table.adjustSize()
    table.setColumnWidth(0, 260)
