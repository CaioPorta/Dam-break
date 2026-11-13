# -*- coding: utf-8 -*-
"""
Dam Break Control Application - Main Interface

Created for Professor Geraldo de Freitas Maciel - UNESP/FEIS
Author: Caio Porta (CaioPorta)
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import sys
import os
import glob
import csv
import tkinter as tk
from tkinter import filedialog
from time import sleep

# ---------------------------------------------------------------------------
# PyQt5
# ---------------------------------------------------------------------------
from PyQt5.QtGui import (
    QFont, QBrush, QColor, QIcon, QCursor, QKeyEvent,
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QRadioButton,
    QButtonGroup, QGridLayout, QVBoxLayout, QHBoxLayout,
    QMessageBox, QInputDialog, QAbstractScrollArea, QSizePolicy,
)
from PyQt5.QtCore import Qt, QEvent, QThread, QSize

# ---------------------------------------------------------------------------
# Local modules
# ---------------------------------------------------------------------------
from DBManager import DBManager
from ArduinoComm import ArduinoComm
from WorkerThread import WorkerThread
from config import (
    APP_VERSION_INFO, PARAM_LIMITS, PRECISION_OPTIONS, DEFAULT_PRECISION,
    SCREEN_RATIOS, THEMES, FONTS, ICON_PATH, SAVE_ICON, ARDUINO_ICON,
    INFO_ICON, DEFAULT_MACRO_NAMES, PASSWORD, ARDUINO_BAUDRATE,
    ARDUINO_TIMEOUT, THREAD_INTERVAL, MACRO_TABLE_COLUMNS, INPUT_MASKS,
)
from ui_components import (
    ThemeManager,
    create_button,
    create_label,
    create_textbox,
    create_precision_radios,
    build_control_row,
    setup_macro_table,
    setup_history_table,
)


# ---------------------------------------------------------------------------
# Helper: clamp a value to a range
# ---------------------------------------------------------------------------
def _clamp(value, min_val, max_val):
    """Return *value* clamped to the [*min_val*, *max_val*] range."""
    return max(min_val, min(value, max_val))


# ---------------------------------------------------------------------------
# Helper: find the closest value in a list
# ---------------------------------------------------------------------------
def _closest(lst, target):
    """Return the element in *lst* closest to *target*."""
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - target))]


# ---------------------------------------------------------------------------
# Main HMI class
# ---------------------------------------------------------------------------
class IHMmain(QWidget):
    """Main interface for the Dam Break control system."""

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IHM")

        # -- App metadata --
        self.app_version_info = APP_VERSION_INFO

        # -- Subsystems --
        self.db_manager = DBManager(self)
        self.arduino_comm = ArduinoComm(self)
        self.theme_manager = ThemeManager(self)

        # -- Screen metrics (set in _init_screen_metrics) --
        self.screen_width = 0
        self.screen_height = 0

        # -- Font cache --
        self._fonts = {}

        # -- Parameter state --
        self.acceleration = 0.0
        self.velocity = 0.0
        self.position = 0.0
        self.inclination = 0.0

        self.max_acceleration = PARAM_LIMITS["acceleration"]["max"]
        self.min_acceleration = PARAM_LIMITS["acceleration"]["min"]
        self.max_velocity = PARAM_LIMITS["velocity"]["max"]
        self.min_velocity = PARAM_LIMITS["velocity"]["min"]
        self.max_position = PARAM_LIMITS["position"]["max"]
        self.min_position = PARAM_LIMITS["position"]["min"]
        self.max_inclination = PARAM_LIMITS["inclination"]["max"]
        self.min_inclination = PARAM_LIMITS["inclination"]["min"]

        self.precision = DEFAULT_PRECISION
        self.precision_acceleration = 0.1
        self.precision_velocity = 0.1
        self.precision_position = 0.1
        self.precision_inclination = 0.5

        # -- UI state --
        self.macro_running = False
        self.file_dialog_open = False
        self.recording_mode = "normal"  # "normal" or "Gravar"
        self.password = PASSWORD
        self.background_style = "Bright"

        # -- Worker thread control --
        self.abort_thread = False

        # -- Macro editor data --
        self.macro_data = []
        self.macro_names = self.db_manager.get_macro_names()

        # -- Widget references (populated by _build_ui) --
        self._widgets = {}

        # -- Initialize screen metrics --
        self._init_screen_metrics()

        # -- Build UI --
        self._setup_base_window()
        self._build_ui()

        # -- Restore cached values --
        self._restore_cached_values()

        # -- Connect Arduino to last used port --
        last_port = self.db_manager.get_cache_port()
        if last_port:
            self.arduino_comm.connect(last_port)

        # -- Install event filter for resize handling --
        self.installEventFilter(self)

    # ------------------------------------------------------------------
    # Screen & font initialization
    # ------------------------------------------------------------------
    def _init_screen_metrics(self):
        """Initialize screen dimensions and font cache."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            self.screen_width = user32.GetSystemMetrics(0)
            self.screen_height = user32.GetSystemMetrics(1)
        except Exception:
            self.screen_width = 1920
            self.screen_height = 1080

        for key, (name, size, bold) in FONTS.items():
            font = QFont(name, size)
            font.setBold(bold)
            self._fonts[key] = font

    # ------------------------------------------------------------------
    # Base window setup
    # ------------------------------------------------------------------
    def _setup_base_window(self):
        """Configure the main window properties."""
        self.setWindowTitle("Dambreak")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setAutoFillBackground(True)
        min_w = int(self.screen_width * 0.55)
        min_h = int(self.screen_height * 0.75)
        self.setMinimumSize(QSize(min_w, min_h))
        self.showMaximized()

        # Apply initial theme
        bg_color = THEMES[self.background_style]["background"]
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(bg_color))
        self.setPalette(palette)

    # ------------------------------------------------------------------
    # UI building
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Build the complete UI layout."""
        grid = QGridLayout()
        self.setLayout(grid)
        self._grid = grid

        if self.recording_mode == "Gravar":
            self._build_macro_editor_layout(grid)
        else:
            self._build_main_layout(grid)

    # ------------------------------------------------------------------
    # Main layout (normal mode)
    # ------------------------------------------------------------------
    def _build_main_layout(self, grid):
        """Build the main layout with macros, commands, and status panels."""
        # -- Title bar --
        title = create_label("Controle de Dambreak", "largest")
        title.setFixedHeight(int(self.screen_height * SCREEN_RATIOS["title_height"]))

        grid.addWidget(title, 0, 0, 1, 3, Qt.AlignCenter)

        # -- Theme toggle button --
        theme_btn = create_button()
        theme_btn.setFixedWidth(int(self.screen_width * SCREEN_RATIOS["theme_button_width"]))
        theme_btn.setIcon(QIcon(ICON_PATH))
        theme_btn.setIconSize(QSize(
            int(self.frameGeometry().height() / 15),
            int(self.frameGeometry().height() / 15),
        ))
        theme_btn.pressed.connect(lambda: self._handle_command("Mudar tema"))
        grid.addWidget(theme_btn, 0, 0, 1, 3, Qt.AlignLeft | Qt.AlignTop)

        # -- Panels --
        macros_layout = self._build_macros_panel()
        commands_layout = self._build_commands_panel()
        status_layout = self._build_status_panel()

        # -- Top-right buttons --
        clear_db_btn = self._create_clear_db_button()
        version_btn = self._create_version_button()
        arduino_btn = self._create_arduino_button()

        grid.addWidget(create_label("Macros", "section"), 1, 0, Qt.AlignHCenter)
        grid.addLayout(macros_layout, 2, 0, Qt.AlignHCenter)

        grid.addWidget(create_label("Comandos manuais", "section"), 1, 1, Qt.AlignHCenter)
        grid.addLayout(commands_layout, 2, 1, Qt.AlignHCenter)

        grid.addWidget(create_label("Status", "section"), 1, 2, Qt.AlignHCenter)
        grid.addLayout(status_layout, 2, 2, Qt.AlignHCenter)

        grid.addWidget(clear_db_btn, 0, 2, Qt.AlignTop | Qt.AlignRight)
        grid.addWidget(version_btn, 0, 2, Qt.AlignBottom | Qt.AlignRight)
        grid.addWidget(arduino_btn, 0, 2, Qt.AlignTop | Qt.AlignRight)

    # ------------------------------------------------------------------
    # Macros panel
    # ------------------------------------------------------------------
    def _build_macros_panel(self):
        """Build the macros panel with 8 macro buttons."""
        layout = QVBoxLayout()
        layout.setSpacing(50)

        macro_btns_layout = QHBoxLayout()
        self._macro_buttons = []

        for i in range(8):
            btn_text = self.macro_names[i] if i < len(self.macro_names) else f"Macro{i + 1}"
            btn = create_button(btn_text, font_key="xxlarge")
            btn_size = int(self.frameGeometry().height() * SCREEN_RATIOS["button_size"])
            btn.setFixedSize(btn_size, btn_size)
            btn.pressed.connect(lambda checked, idx=i: self._handle_command(f"Macro{idx + 1}"))
            self._macro_buttons.append(btn)
            macro_btns_layout.addWidget(btn)

        # Arrange in rows of 2
        for row in range(4):
            row_layout = QHBoxLayout()
            for col in range(2):
                idx = row * 2 + col
                if idx < 8:
                    row_layout.addWidget(self._macro_buttons[idx])
            layout.addLayout(row_layout)

        # Spacer
        spacer = QLabel("")
        spacer.setFixedHeight(int(self.screen_height * SCREEN_RATIOS["spacer_height"]))
        layout.addWidget(spacer)

        # Record / Delete buttons
        record_btn = create_button("Editar\nmacros", "large")
        record_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        record_btn.pressed.connect(lambda: self._handle_command("GravarMacro"))

        delete_macro_btn = create_button("Deletar\nmacros", "large")
        delete_macro_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        delete_macro_btn.pressed.connect(lambda: self._handle_command("DeletarMacro"))

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(record_btn)
        bottom_layout.addWidget(delete_macro_btn)
        layout.addLayout(bottom_layout)

        return layout

    # ------------------------------------------------------------------
    # Commands panel
    # ------------------------------------------------------------------
    def _build_commands_panel(self):
        """Build the manual commands panel."""
        layout = QVBoxLayout()

        # -- Precision selection --
        layout.addWidget(create_label("Precisao", "xlarge"))
        self._precision_radios, self._precision_group = create_precision_radios(
            PRECISION_OPTIONS, self
        )
        prec_layout = QHBoxLayout()
        for radio in self._precision_radios:
            prec_layout.addWidget(radio)
        layout.addLayout(prec_layout)

        # -- Parameter controls --
        self._text_boxes = {}
        self._increment_buttons = {}
        self._decrement_buttons = {}
        self._max_buttons = {}
        self._med_buttons = {}
        self._min_buttons = {}

        params = [
            ("acceleration", "Aceleracao max", "MaisAceleracao", "MenosAceleracao",
             "MaxAceleracao", "MedAceleracao", "MinAceleracao"),
            ("velocity", "Velocidade max", "MaisVelocidade", "MenosVelocidade",
             "MaxVelocidade", "MedVelocidade", "MinVelocidade"),
            ("position", "Ir para posicao", "MaisPosicao", "MenosPosicao",
             "MaxPosicao", "MedPosicao", "MinPosicao"),
            ("inclination", "Ir para inclinacao", "MaisInclinacao", "MenosInclinacao",
             "MaxInclinacao", "MedInclinacao", "MinInclinacao"),
        ]

        for param_key, label_text, inc_cmd, dec_cmd, max_cmd, med_cmd, min_cmd in params:
            textbox = create_textbox(
                text=str(getattr(self, param_key)),
                font_key="medium",
                input_mask=INPUT_MASKS[param_key],
            )
            textbox.setEnabled(False)
            textbox.setFixedWidth(int(self.frameGeometry().width() * SCREEN_RATIOS["text_field_width"]))
            self._text_boxes[param_key] = textbox

            inc_btn = create_button("+", "large")
            inc_btn.setFixedWidth(int(self.frameGeometry().width() / 20))
            inc_btn.pressed.connect(lambda checked, c=inc_cmd: self._handle_command(c))
            inc_btn.released.connect(lambda checked, c=inc_cmd: self._handle_command(f"{c}Released"))
            self._increment_buttons[param_key] = inc_btn

            dec_btn = create_button("-", "large")
            dec_btn.setFixedWidth(int(self.frameGeometry().width() / 20))
            dec_btn.pressed.connect(lambda checked, c=dec_cmd: self._handle_command(c))
            dec_btn.released.connect(lambda checked, c=dec_cmd: self._handle_command(f"{c}Released"))
            self._decrement_buttons[param_key] = dec_btn

            max_btn = create_button("Max", "large")
            max_btn.setFixedWidth(int(self.frameGeometry().width() / 15))
            max_btn.pressed.connect(lambda checked, c=max_cmd: self._handle_command(c))
            self._max_buttons[param_key] = max_btn

            med_btn = create_button("Med", "large")
            med_btn.setFixedWidth(int(self.frameGeometry().width() / 15))
            med_btn.pressed.connect(lambda checked, c=med_cmd: self._handle_command(c))
            self._med_buttons[param_key] = med_btn

            min_btn = create_button("Min", "large")
            min_btn.setFixedWidth(int(self.frameGeometry().width() / 15))
            min_btn.pressed.connect(lambda checked, c=min_cmd: self._handle_command(c))
            self._min_buttons[param_key] = min_btn

            build_control_row(
                self, param_key, label_text, textbox,
                inc_btn, dec_btn, max_btn, med_btn, min_btn, layout,
            )

            # Connect text change handler
            textbox.textChanged.connect(lambda text, p=param_key: self._on_value_changed(p, text))

        # Spacer
        spacer = QLabel("")
        spacer.setFixedHeight(int(self.screen_height * SCREEN_RATIOS["spacer_height"]))
        layout.addWidget(spacer)

        # Execute button
        execute_btn = create_button("Executar\ncomando", "heading")
        execute_btn.setFixedWidth(int(self.frameGeometry().width() * SCREEN_RATIOS["execute_button_width"]))
        execute_btn.setFixedHeight(int(self.screen_height / 10))
        execute_btn.setStyleSheet("background-color: green; border: none; outline: none;")
        execute_btn.pressed.connect(lambda: self._handle_command("Executar"))
        layout.addWidget(execute_btn, alignment=Qt.AlignHCenter)

        return layout

    # ------------------------------------------------------------------
    # Status panel
    # ------------------------------------------------------------------
    def _build_status_panel(self):
        """Build the status panel showing current values and command history."""
        layout = QVBoxLayout()

        self.label_position = create_label(
            f"Posicao atual\n{self.position}mm", "xlarge"
        )
        self.label_inclination = create_label(
            f"Inclinacao atual\n{self.inclination}\u00b0", "xlarge"
        )
        self.label_history = create_label("Historico de comandos", "xlarge")

        self.history_table = QTableWidget()
        self.history_data = self.db_manager.get_all_moves()[::-1]
        setup_history_table(self.history_table, self.history_data, self.screen_width)

        layout.addWidget(self.label_position)
        layout.addWidget(self.label_inclination)
        layout.addWidget(self.label_history)
        layout.addWidget(self.history_table)

        return layout

    # ------------------------------------------------------------------
    # Macro editor layout (recording mode)
    # ------------------------------------------------------------------
    def _build_macro_editor_layout(self, grid):
        """Build the macro editor layout (shown when recording macros)."""
        # -- Title bar --
        title = create_label("Controle de Dambreak", "largest")
        title.setFixedHeight(int(self.screen_height * SCREEN_RATIOS["title_height"]))
        grid.addWidget(title, 0, 0, 1, 3, Qt.AlignCenter)

        # -- Theme toggle --
        theme_btn = create_button()
        theme_btn.setFixedWidth(int(self.screen_width * SCREEN_RATIOS["theme_button_width"]))
        theme_btn.setIcon(QIcon(ICON_PATH))
        theme_btn.setIconSize(QSize(
            int(self.frameGeometry().height() / 15),
            int(self.frameGeometry().height() / 15),
        ))
        theme_btn.pressed.connect(lambda: self._handle_command("Mudar tema"))
        grid.addWidget(theme_btn, 0, 0, 1, 3, Qt.AlignLeft | Qt.AlignTop)

        # -- Macro panel --
        macros_layout = QVBoxLayout()
        macros_layout.setSpacing(50)

        # Macro name combobox
        self.macro_combobox = QComboBox()
        self.macro_combobox.setStyleSheet("background-color: white; border: none; outline: none;")
        self.macro_combobox.setFixedWidth(int(self.frameGeometry().width() * SCREEN_RATIOS["macro_panel_width"]))
        self._macro_edit = QLineEdit(self)
        self._macro_edit.setFont(self._fonts["xlarge"])
        self._macro_edit.setStyleSheet("background-color: white; border: none; outline: none;")
        self._macro_edit.setAlignment(Qt.AlignCenter)
        self._macro_edit.returnPressed.connect(lambda: self._handle_command("ComboBox_Macros"))
        self.macro_combobox.setLineEdit(self._macro_edit)
        self.macro_combobox.setFont(self._fonts["xlarge"])
        self.macro_combobox.setCursor(QCursor(Qt.PointingHandCursor))
        for name in self.db_manager.get_macro_names():
            self.macro_combobox.addItem(name)
        macros_layout.addWidget(self.macro_combobox)

        # Macro table
        self.macro_table = QTableWidget()
        self.macro_data = self.db_manager.get_macro_moves(self.macro_combobox.currentIndex())
        if self.macro_data:
            self._cycles_textbox.setText(str(self.macro_data[0][5]))
        setup_macro_table(self.macro_table, self.macro_data, SCREEN_RATIOS["macro_panel_width"])
        macros_layout.addWidget(self.macro_table)

        # Record / Delete action buttons
        del_action_btn = create_button("Deletar\nultima acao", "heading")
        del_action_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        del_action_btn.setStyleSheet("background-color: red; border: none; outline: none;")
        del_action_btn.pressed.connect(lambda: self._handle_command("DeletarAcao"))

        reg_action_btn = create_button("Registrar\nultima acao", "heading")
        reg_action_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        reg_action_btn.setStyleSheet("background-color: green; border: none; outline: none;")
        reg_action_btn.pressed.connect(lambda: self._handle_command("RegistrarAcao"))

        row1 = QHBoxLayout()
        row1.addWidget(del_action_btn)
        row1.addWidget(reg_action_btn)
        macros_layout.addLayout(row1)

        # Cycle count and test button
        self._cycles_textbox = create_textbox("1", "large", "99 ciclos")
        self._cycles_textbox.setFixedWidth(int(self.frameGeometry().width() / 7))
        self._cycles_textbox.textChanged.connect(self._on_cycles_changed)

        test_btn = create_button("Testar\nmacro", "heading")
        test_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        test_btn.pressed.connect(lambda: self._handle_command("TestarMacro"))

        row2 = QHBoxLayout()
        row2.addWidget(self._cycles_textbox)
        row2.addWidget(test_btn)
        macros_layout.addLayout(row2)

        # Save / Cancel buttons
        save_btn = create_button("Gravar\nmacro", "heading")
        save_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        save_btn.pressed.connect(lambda: self._handle_command("RegistrarMacro"))

        cancel_btn = create_button("Cancelar\ngravacao", "heading")
        cancel_btn.setFixedWidth(int(self.frameGeometry().width() / 7))
        cancel_btn.pressed.connect(lambda: self._handle_command("CancelarMacro"))

        row3 = QHBoxLayout()
        row3.addWidget(save_btn)
        row3.addWidget(cancel_btn)
        macros_layout.addLayout(row3)

        grid.addWidget(create_label("Macros", "section"), 1, 0, Qt.AlignHCenter)
        grid.addLayout(macros_layout, 2, 0, Qt.AlignHCenter)

        # -- Commands panel (same as main) --
        commands_layout = self._build_commands_panel()
        grid.addWidget(create_label("Comandos manuais", "section"), 1, 1, Qt.AlignHCenter)
        grid.addLayout(commands_layout, 2, 1, Qt.AlignHCenter)

        # -- Status panel --
        status_layout = self._build_status_panel()
        grid.addWidget(create_label("Status", "section"), 1, 2, Qt.AlignHCenter)
        grid.addLayout(status_layout, 2, 2, Qt.AlignHCenter)

        # -- Top-right buttons --
        clear_db_btn = self._create_clear_db_button()
        version_btn = self._create_version_button()
        arduino_btn = self._create_arduino_button()
        grid.addWidget(clear_db_btn, 0, 2, Qt.AlignTop | Qt.AlignRight)
        grid.addWidget(version_btn, 0, 2, Qt.AlignBottom | Qt.AlignRight)
        grid.addWidget(arduino_btn, 0, 2, Qt.AlignTop | Qt.AlignRight)

    # ------------------------------------------------------------------
    # Button factory helpers
    # ------------------------------------------------------------------
    def _create_clear_db_button(self):
        """Create the database clear button."""
        btn = create_button()
        btn.setFixedWidth(int(self.screen_width * SCREEN_RATIOS["theme_button_width"]))
        btn.setIcon(QIcon(THEMES[self.background_style]["clear_db_icon"]))
        btn.setIconSize(QSize(
            int(self.frameGeometry().height() / 20),
            int(self.frameGeometry().height() / 20),
        ))
        btn.pressed.connect(lambda: self._handle_command("LimparDB"))
        return btn

    def _create_version_button(self):
        """Create the version info button."""
        btn = create_button()
        btn.setIcon(QIcon(INFO_ICON))
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet("background-color: none; border: none; outline: none;")
        btn.pressed.connect(
            lambda: QMessageBox.about(self, "Informacoes da versao do APP", self.app_version_info)
        )
        return btn

    def _create_arduino_button(self):
        """Create the Arduino connect button."""
        btn = create_button()
        btn.setIcon(QIcon(ARDUINO_ICON))
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet("background-color: none; border: none; outline: none;")
        btn.pressed.connect(lambda: self._handle_command("ArduinoConnect"))
        return btn

    # ------------------------------------------------------------------
    # Cached values restoration
    # ------------------------------------------------------------------
    def _restore_cached_values(self):
        """Restore parameter values from the database cache."""
        self.precision = self.db_manager.get_cache_precision()
        self.acceleration = self.db_manager.get_cache_acceleration()
        self.velocity = self.db_manager.get_cache_velocity()
        self.position = self.db_manager.get_cache_position()
        self.inclination = self.db_manager.get_cache_inclination()

        # Set precision radio
        for radio in self._precision_radios:
            if radio.text() == self.precision:
                radio.setChecked(True)
                break

        # Update text boxes
        self._text_boxes["acceleration"].setText(str(self.acceleration))
        self._text_boxes["velocity"].setText(str(self.velocity))
        self._text_boxes["position"].setText(str(self.position))
        self._text_boxes["inclination"].setText(str(self.inclination))

    # ------------------------------------------------------------------
    # Theme application
    # ------------------------------------------------------------------
    def _apply_theme(self):
        """Apply the current theme to all widgets."""
        theme = self.theme_manager.current_theme
        bg = theme["background"]
        bg2 = theme["background_secondary"]
        font_color = theme["font"]

        # Window palette
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(bg))
        self.setPalette(palette)

        # Title and section labels
        for attr in ["label_position", "label_inclination", "label_history"]:
            widget = getattr(self, attr, None)
            if widget and isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {font_color}")

        # Update clear DB icon
        clear_db_btn = self._widgets.get("clear_db_btn")
        if clear_db_btn:
            clear_db_btn.setIcon(QIcon(theme["clear_db_icon"]))

        # Update all buttons
        for btn in self._macro_buttons:
            btn.setStyleSheet(f"background-color: {bg2}; border: none; outline: none;")

        # Update text boxes
        for textbox in self._text_boxes.values():
            textbox.setStyleSheet(f"background-color: {bg2}; color: black; border: none; outline: none;")

        # Update precision radios
        for radio in self._precision_radios:
            radio.setStyleSheet(f"background-color: {bg2}; border: none; outline: none;")

        # Update combobox
        if hasattr(self, "macro_combobox"):
            self.macro_combobox.setStyleSheet(f"background-color: {bg2}; border: none; outline: none;")
        if hasattr(self, "_macro_edit"):
            self._macro_edit.setStyleSheet(f"background-color: {bg2}; border: none; outline: none;")

        # Update cycle textbox
        if hasattr(self, "_cycles_textbox"):
            self._cycles_textbox.setStyleSheet(f"background-color: {bg2}; border: none; outline: none;")

    # ------------------------------------------------------------------
    # Command dispatch (replaces the giant if-elif chain)
    # ------------------------------------------------------------------
    def _handle_command(self, command_name):
        """Dispatch a command to the appropriate handler.

        Parameters
        ----------
        command_name : str
            The command identifier (e.g. "Macro1", "MaisAceleracao", etc.).
        """
        handler = self._get_command_handler(command_name)
        if handler:
            handler()

    def _get_command_handler(self, command_name):
        """Return the handler method for a given command, or None."""
        # Theme
        if command_name == "Mudar tema":
            return self._handle_theme

        # Macro execution (Macro1-Macro8)
        if command_name.startswith("Macro") and command_name[5:].isdigit():
            macro_idx = int(command_name[5]) - 1
            return lambda: self._execute_macro(macro_idx)

        # Macro management
        if command_name == "GravarMacro":
            return self._handle_gravar_macro
        if command_name == "DeletarMacro":
            return self._handle_deletar_macro

        # Parameter increment/decrement (button press)
        inc_map = {
            "MaisAceleracao": "acceleration",
            "MaisVelocidade": "velocity",
            "MaisPosicao": "position",
            "MaisInclinacao": "inclination",
        }
        if command_name in inc_map:
            return lambda param=inc_map[command_name]: self._start_increment_thread(param)

        dec_map = {
            "MenosAceleracao": "acceleration",
            "MenosVelocidade": "velocity",
            "MenosPosicao": "position",
            "MenosInclinacao": "inclination",
        }
        if command_name in dec_map:
            return lambda param=dec_map[command_name]: self._start_decrement_thread(param)

        # Parameter increment/decrement (button release - stop thread)
        if command_name.endswith("Released"):
            return self._stop_threads

        # Max/Med/Min buttons
        max_map = {
            "MaxAceleracao": ("acceleration", lambda s: s.max_acceleration),
            "MaxVelocidade": ("velocity", lambda s: s.max_velocity),
            "MaxPosicao": ("position", lambda s: s.max_position),
            "MaxInclinacao": ("inclination", lambda s: s.max_inclination),
        }
        if command_name in max_map:
            param, getter = max_map[command_name]
            return lambda p=param, g=getter: self._set_parameter(p, g(self))

        med_map = {
            "MedAceleracao": ("acceleration", "max_acceleration", "min_acceleration"),
            "MedVelocidade": ("velocity", "max_velocity", "min_velocity"),
            "MedPosicao": ("position", "max_position", "min_position"),
            "MedInclinacao": ("inclination", "max_inclination", "min_inclination"),
        }
        if command_name in med_map:
            param, max_attr, min_attr = med_map[command_name]
            return lambda p=param, ma=max_attr, mi=min_attr: self._set_parameter(
                p, lambda s: round((getattr(s, ma) + getattr(s, mi)) / 2, 1)
            )

        min_map = {
            "MinAceleracao": ("acceleration", lambda s: s.min_acceleration),
            "MinVelocidade": ("velocity", lambda s: s.min_velocity),
            "MinPosicao": ("position", lambda s: s.min_position),
            "MinInclinacao": ("inclination", lambda s: s.min_inclination),
        }
        if command_name in min_map:
            param, getter = min_map[command_name]
            return lambda p=param, g=getter: self._set_parameter(p, g(self))

        # Execute command
        if command_name == "Executar":
            return self._handle_executar

        # Database
        if command_name == "LimparDB":
            return self._handle_limpar_db

        # ComboBox
        if command_name == "ComboBox_Macros":
            return self._handle_combo_macros

        # Macro editor actions
        if command_name == "DeletarAcao":
            return self._handle_deletar_acao
        if command_name == "RegistrarAcao":
            return self._handle_registrar_acao
        if command_name == "TestarMacro":
            return self._handle_testar_macro
        if command_name == "CancelarMacro":
            return self._handle_cancelar_macro
        if command_name == "RegistrarMacro":
            return self._handle_registrar_macro

        # Arduino
        if command_name == "ArduinoConnect":
            return self._handle_arduino_connect

        return None

    # ------------------------------------------------------------------
    # Command handler implementations
    # ------------------------------------------------------------------
    def _handle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()
        self.background_style = self.theme_manager.current_theme_name
        self._apply_theme()

    def _execute_macro(self, macro_index):
        """Execute a macro by index."""
        self.macro_executor.execute(macro_index)

    def _handle_gravar_macro(self):
        """Enter macro recording mode."""
        senha, done = QInputDialog.getText(self, "Gravar macro", "Senha:", QLineEdit.Password)
        if done and senha == self.password:
            self._switch_to_recording_mode()

    def _handle_deletar_macro(self):
        """Delete a macro."""
        senha, done = QInputDialog.getText(self, "Deletar macro", "Senha:", QLineEdit.Password)
        if not (done and senha == self.password):
            return

        macro_names = self.db_manager.get_macro_names()
        macro_name, done = QInputDialog.getItem(
            self, "Deletar Macro", "Macro a ser zerada:", macro_names, False
        )
        if not done:
            return

        idx = macro_names.index(macro_name)
        # Check if the auto-generated name would conflict
        other_names = [
            name for i, name in enumerate(self.db_manager.get_macro_names())
            if name == f"Macro{idx + 1}" and i != idx
        ]
        if other_names:
            QMessageBox.warning(
                self, "Erro",
                f"Existe outra macro com o nome que essa deveria receber\n(Macro{idx + 1})"
            )
            return

        self.db_manager.overwrite_macro(idx, [])
        self.db_manager.set_macro_name(idx, f"Macro{idx + 1}")

        # Refresh macro button names
        self.macro_names = self.db_manager.get_macro_names()
        for i, name in enumerate(self.macro_names):
            if i < len(self._macro_buttons):
                self._macro_buttons[i].setText(name)

    # Mapping from parameter key to thread name suffix
    _THREAD_NAMES = {
        "acceleration": ("Thread_MaisAceleracao", "Thread_MenosAceleracao"),
        "velocity": ("Thread_MaisVelocidade", "Thread_MenosVelocidade"),
        "position": ("Thread_MaisPosicao", "Thread_MenosPosicao"),
        "inclination": ("Thread_MaisInclinacao", "Thread_MenosInclinacao"),
    }

    def _start_increment_thread(self, param):
        """Start a worker thread that increments a parameter."""
        self.abort_thread = False
        thread_name = self._THREAD_NAMES[param][0]
        thread = WorkerThread(thread_name, self)
        thread.start()

    def _start_decrement_thread(self, param):
        """Start a worker thread that decrements a parameter."""
        self.abort_thread = False
        thread_name = self._THREAD_NAMES[param][1]
        thread = WorkerThread(thread_name, self)
        thread.start()

    def _stop_threads(self):
        """Stop all worker threads."""
        self.abort_thread = True

    def _set_parameter(self, param, value_getter):
        """Set a parameter to a specific value.

        Parameters
        ----------
        param : str
            Parameter name (e.g. 'acceleration').
        value_getter : callable
            Function that returns the target value, receiving self.
        """
        value = value_getter(self)
        setattr(self, param, value)
        self._text_boxes[param].setText(str(value))

    def _handle_executar(self):
        """Execute the current manual command."""
        if not self.arduino_comm.connected:
            QMessageBox.warning(self, "Erro", "Arduino nao conectado.")
            return

        success = self.arduino_comm.send_command([
            self.position, self.velocity, self.acceleration, self.inclination, 0
        ])
        if success:
            self.db_manager.write_on_db([self.position, self.velocity, self.acceleration, self.inclination])
            self.history_table.clear()
            self.history_data = self.db_manager.get_all_moves()[::-1]
            setup_history_table(self.history_table, self.history_data, self.screen_width)
            self.label_position.setText(f"Posicao atual\n{self.position}mm")
            self.label_inclination.setText(f"Inclinacao atual\n{self.inclination}\u00b0")

    def _handle_limpar_db(self):
        """Clear the command history database."""
        msg = QMessageBox()
        msg.setWindowTitle("Limpar DB")
        msg.setText("Tem certeza que deseja\nlimpar o historico de comandos?")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setWindowIcon(QIcon(ICON_PATH))

        if msg.exec() == QMessageBox.Yes:
            self.db_manager.clear_db()
            self.history_table.clear()
            self.history_data = []

    def _handle_combo_macros(self):
        """Handle macro name changes from the combobox."""
        idx = self.macro_combobox.currentIndex()
        new_name = self.macro_combobox.currentText()
        if len(new_name) < 11:
            existing = [n for n in self.db_manager.get_macro_names() if n == new_name]
            if not existing:
                self.db_manager.set_macro_name(idx, new_name)

        # Refresh combobox
        self.macro_combobox.clear()
        for name in self.db_manager.get_macro_names():
            self.macro_combobox.addItem(name)
        self.macro_combobox.setCurrentIndex(idx)

    def _handle_deletar_acao(self):
        """Remove the last action from the macro editor."""
        self.macro_data = self.macro_data[::-1][:-1][::-1]
        self.macro_table.setRowCount(len(self.macro_data))
        setup_macro_table(self.macro_table, self.macro_data, SCREEN_RATIOS["macro_panel_width"])

    def _handle_registrar_acao(self):
        """Add the last command to the macro editor."""
        last_moves = self.db_manager.get_all_moves()
        if not last_moves:
            QMessageBox.warning(self, "Aviso", "Nao ha comando para registrar.")
            return

        last_move = last_moves[-1]
        cycles = int(self._cycles_textbox.text().replace(" ciclos", ""))
        new_entry = (last_move[0], last_move[1], last_move[2], last_move[3], 1.0, cycles)

        self.macro_data = self.macro_data[::-1]
        self.macro_data.append(new_entry)
        self.macro_data = self.macro_data[::-1]

        self.macro_table.setRowCount(len(self.macro_data))
        setup_macro_table(self.macro_table, self.macro_data, SCREEN_RATIOS["macro_panel_width"])

    def _handle_testar_macro(self):
        """Test the current macro without recording."""
        if not self.arduino_comm.connected:
            QMessageBox.warning(self, "Erro", "Arduino nao conectado.")
            return

        commands = self.macro_data[::-1]
        if not commands:
            return

        for cycle in range(commands[0][5]):
            print(f"Ciclo {cycle + 1}")
            for cmd in commands:
                sleep(cmd[4])
                self.arduino_comm.send_command([cmd[0], cmd[1], cmd[2], cmd[3], 0])

    def _handle_cancelar_macro(self):
        """Exit macro recording mode."""
        self._switch_to_normal_mode()

    def _handle_registrar_macro(self):
        """Save the current macro."""
        self.db_manager.overwrite_macro(self.macro_combobox.currentIndex(), self.macro_data)

        idx = self.macro_combobox.currentIndex()
        new_name = self.macro_combobox.currentText()
        if len(new_name) < 11:
            self.db_manager.set_macro_name(idx, new_name)

        # Refresh macro button names
        self.macro_names = self.db_manager.get_macro_names()
        for i, name in enumerate(self.macro_names):
            if i < len(self._macro_buttons):
                self._macro_buttons[i].setText(name)

        self._switch_to_normal_mode()

    def _handle_arduino_connect(self):
        """Prompt user to select an Arduino port."""
        if sys.platform.startswith("win"):
            ports = [f"COM{i + 1}" for i in range(256)]
        elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
            ports = glob.glob("/dev/tty[A-Za-z]*")
        elif sys.platform.startswith("darwin"):
            ports = glob.glob("/dev/tty.*")
        else:
            QMessageBox.warning(self, "Erro", "Plataforma nao suportada.")
            return

        available_ports = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                available_ports.append(port)
            except (OSError, Exception):
                pass

        if not available_ports:
            QMessageBox.warning(self, "Erro", "Nenhuma porta serial detectada.")
            return

        port, done = QInputDialog.getItem(
            self, "Porta", "Porta onde se encontra o Arduino:", available_ports, False
        )
        if done:
            self.arduino_comm.connect(port)
            if not self.arduino_comm.connected:
                QMessageBox.warning(self, "Erro", "Impossivel se conectar ao arduino.")
            else:
                self.db_manager.update_cache_port(port)

    # ------------------------------------------------------------------
    # UI cleanup
    # ------------------------------------------------------------------
    def _clear_widgets(self):
        """Delete all dynamically created widgets before rebuilding the UI."""
        # Delete all stored widget references
        for name, widget in list(self._widgets.items()):
            if widget is not None:
                widget.deleteLater()
        self._widgets.clear()

        # Delete macro buttons
        for btn in getattr(self, "_macro_buttons", []):
            btn.deleteLater()
        self._macro_buttons = []

        # Delete text boxes
        for tb in getattr(self, "_text_boxes", {}).values():
            tb.deleteLater()
        self._text_boxes = {}

        # Delete increment/decrement buttons
        for btn in getattr(self, "_increment_buttons", {}).values():
            btn.deleteLater()
        for btn in getattr(self, "_decrement_buttons", {}).values():
            btn.deleteLater()
        self._increment_buttons = {}
        self._decrement_buttons = {}

        # Delete max/med/min buttons
        for btn in getattr(self, "_max_buttons", {}).values():
            btn.deleteLater()
        for btn in getattr(self, "_med_buttons", {}).values():
            btn.deleteLater()
        for btn in getattr(self, "_min_buttons", {}).values():
            btn.deleteLater()
        self._max_buttons = {}
        self._med_buttons = {}
        self._min_buttons = {}

        # Delete precision radios
        for radio in getattr(self, "_precision_radios", []):
            radio.deleteLater()
        group = getattr(self, "_precision_group", None)
        if group:
            group.deleteLater()
        self._precision_radios = []
        self._precision_group = None

        # Delete layout widgets from the grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------
    def _switch_to_recording_mode(self):
        """Switch to macro recording mode."""
        self._clear_widgets()
        self.recording_mode = "Gravar"
        self._build_ui()

    def _switch_to_normal_mode(self):
        """Switch to normal mode."""
        self._clear_widgets()
        self.recording_mode = "normal"
        self.macro_names = self.db_manager.get_macro_names()
        self._build_ui()

    # ------------------------------------------------------------------
    # Value change handlers
    # ------------------------------------------------------------------
    def _on_value_changed(self, param_key, text):
        """Handle text box value changes.

        Parameters
        ----------
        param_key : str
            Parameter name.
        text : str
            New text value.
        """
        limits = PARAM_LIMITS[param_key]
        min_val = limits["min"]
        max_val = limits["max"]

        try:
            # Extract numeric value from the text (strip unit suffix)
            text_clean = text
            for suffix in ["mm/s²", "mm/s", "mm", "°"]:
                text_clean = text_clean.replace(suffix, "")

            if not text_clean.strip():
                return

            value = float(text_clean)
            clamped = _clamp(value, min_val, max_val)
            setattr(self, param_key, round(clamped, 1))

            # Update the text box if clamped
            if clamped != value:
                self._text_boxes[param_key].setText(str(clamped))

            # Update database cache
            cache_method_name = f"update_cache_{param_key}"
            cache_method = getattr(self.db_manager, cache_method_name)
            cache_method(round(clamped, 1))

        except (ValueError, AttributeError):
            pass

    def _on_cycles_changed(self, text):
        """Handle cycle count changes."""
        try:
            cycles_text = text.replace(" ciclos", "")
            cycles = int(cycles_text)
            if cycles < 0:
                cycles = 1
                self._cycles_textbox.setText(str(cycles))
        except ValueError:
            cycles = 1

        # Update cycle count in all macro data entries
        self.macro_data = self.macro_data[::-1]
        for idx, cmd in enumerate(self.macro_data):
            self.macro_data[idx] = (cmd[0], cmd[1], cmd[2], cmd[3], cmd[4], cycles)
        self.macro_data = self.macro_data[::-1]

    # ------------------------------------------------------------------
    # Table data insertion helpers
    # ------------------------------------------------------------------
    def insert_data_in_history_table(self):
        """Refresh the command history table."""
        self.history_data = self.db_manager.get_all_moves()[::-1]
        setup_history_table(self.history_table, self.history_data, self.screen_width)

    # ------------------------------------------------------------------
    # Event filter (resize handling)
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        """Handle resize events to adjust widget sizes dynamically."""
        if event.type() == QEvent.Resize:
            self._on_resize()
        return False

    def _on_resize(self):
        """Recompute sizes for widgets that depend on window dimensions."""
        fw = self.frameGeometry().width()
        fh = self.frameGeometry().height()

        # Macro buttons
        btn_size = int(fh * SCREEN_RATIOS["button_size"])
        for btn in self._macro_buttons:
            btn.setFixedSize(btn_size, btn_size)

        # Theme button
        theme_btn = self._widgets.get("theme_btn")
        if theme_btn:
            theme_btn.setFixedWidth(int(self.screen_width * SCREEN_RATIOS["theme_button_width"]))

        # Text boxes
        for textbox in self._text_boxes.values():
            textbox.setFixedWidth(int(fw * SCREEN_RATIOS["text_field_width"]))

        # History table
        if hasattr(self, "history_table"):
            self.history_table.setFixedWidth(int(fw * SCREEN_RATIOS["history_table_width"]))

        # Macro table
        if hasattr(self, "macro_table"):
            self.macro_table.setFixedWidth(int(fw * SCREEN_RATIOS["macro_panel_width"]))
            col_width = int(fw * SCREEN_RATIOS["macro_panel_width"] / 5)
            for i in range(5):
                self.macro_table.setColumnWidth(i, col_width)

        # Cycle textbox
        if hasattr(self, "_cycles_textbox"):
            self._cycles_textbox.setFixedWidth(int(fw / 7))

        # Macro combobox
        if hasattr(self, "macro_combobox"):
            self.macro_combobox.setFixedWidth(int(fw * SCREEN_RATIOS["macro_panel_width"]))

    # ------------------------------------------------------------------
    # Keyboard handler for macro table
    # ------------------------------------------------------------------
    def table_on_key_release_event(self, event):
        """Handle key release in the macro table."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            row = self.macro_table.currentIndex().row()
            col = self.macro_table.currentIndex().column()
            if col == 4:  # Delay column
                new_delay = float(self.macro_table.currentItem().text())
                old = self.macro_data[row]
                self.macro_data[row] = (old[0], old[1], old[2], old[3], new_delay)


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------
class GraphicalThread:
    """Manages the Qt application lifecycle."""

    def __init__(self):
        self.mihm = None
        self.app = None

    def run(self):
        """Start the application."""
        self.app = QApplication(sys.argv)
        self.app.setStyle("fusion")
        try:
            self.mihm = IHMmain()
            self.app.exec_()
            self.mihm.arduino_comm.close()
            self.mihm.db_manager.disconnect()
        except Exception as error:
            print(f"Erro critico: \n{error}")
            if self.mihm:
                self.mihm.arduino_comm.close()
                self.mihm.db_manager.disconnect()
            self.app.quit()
            sys.exit()


if __name__ == "__main__":
    mgraphical_thread = GraphicalThread()
    mgraphical_thread.run()
