# -*- coding: utf-8 -*-
"""
Macro execution and management logic.
"""

import csv
import sys
import tkinter as tk
from tkinter import filedialog

from PyQt5.QtWidgets import QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon

from config import SAVE_ICON, CSV_HEADER


class MacroExecutor:
    """Handles execution of recorded macro sequences."""

    def __init__(self, hmi):
        self.hmi = hmi

    def execute(self, macro_index):
        """Execute a macro by its index (0-7).

        Parameters
        ----------
        macro_index : int
            Index of the macro to execute (0 for Macro1, 1 for Macro2, etc.).

        Returns
        -------
        bool
            True if execution started successfully, False otherwise.
        """
        hmi = self.hmi

        # Precondition checks
        if not hmi.arduino_comm.connected:
            QMessageBox.warning(hmi, "Erro", "Arduino não conectado.")
            return False

        if hmi.macro_running:
            QMessageBox.warning(hmi, "Erro", "Uma macro já está em execução.")
            return False

        # Retrieve macro commands from database
        commands = hmi.db_manager.get_macro_moves(macro_index)
        if not commands:
            QMessageBox.warning(hmi, "Aviso", "Não há nada registrado nessa macro.")
            return False

        # Reverse command order for execution
        commands = commands[::-1]

        # Mark as running
        hmi.macro_running = True

        # Ask user if they want to save to CSV
        save_path = self._prompt_csv_export(macro_index, commands)
        if save_path is None:
            # User declined CSV export; continue without saving
            pass

        # Execute the macro
        self._run_macro_sequence(commands, save_path, macro_index)

        # Reset state
        hmi.macro_running = False
        return True

    def _prompt_csv_export(self, macro_index, commands):
        """Prompt the user to save macro execution data to a CSV file.

        Parameters
        ----------
        macro_index : int
            Index of the macro being executed.
        commands : list of tuples
            The macro commands.

        Returns
        -------
        str or None
            File path if user chooses to save, None otherwise.
        """
        hmi = self.hmi

        msg_box = QMessageBox()
        msg_box.setWindowTitle("Salvar em CSV")
        msg_box.setText("Deseja salvar os comandos em um arquivo CSV?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setWindowIcon(QIcon(SAVE_ICON))

        result = msg_box.exec()
        if result != QMessageBox.Yes:
            return None

        # Show file save dialog
        root = tk.Tk()
        root.withdraw()
        if hmi.file_dialog_open:
            return None
        hmi.file_dialog_open = True

        file_path = filedialog.asksaveasfilename(
            title="Selecione a pasta para salvar seu resultado CSV",
            filetypes=[("CSV files", "*.csv")],
        )
        hmi.file_dialog_open = False
        root.destroy()

        if not file_path:
            hmi.macro_running = False
            QMessageBox.warning(
                hmi, "Aviso",
                "Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado."
            )
            return None

        return file_path

    def _run_macro_sequence(self, commands, save_path, macro_index):
        """Run the macro command sequence.

        Parameters
        ----------
        commands : list of tuples
            Macro commands (position, velocity, acceleration, inclination, delay).
        save_path : str or None
            Optional CSV file path to write execution data.
        macro_index : int
            Index of the macro being executed.
        """
        hmi = self.hmi
        f = None
        writer = None

        if save_path:
            macro_name = hmi.macro_names[macro_index] if macro_index < len(hmi.macro_names) else f"Macro{macro_index + 1}"
            f = open(save_path.replace(".csv", "") + ".csv", "w", newline="", encoding="utf-8")
            writer = csv.writer(f)
            writer.writerow([f"Execucao da macro {macro_name}"])

        num_cycles = commands[0][5]  # Cycle count from first command

        for cycle in range(num_cycles):
            print(f"Ciclo {cycle + 1}")
            if writer:
                writer.writerow([f"Ciclo {cycle + 1}"])
                writer.writerow(CSV_HEADER)

            for cmd in commands:
                pos, vel, acc, incl, delay = cmd

                # Log to database
                hmi.db_manager.write_on_db([pos, vel, acc, incl])

                # Update history table
                hmi.history_table.clear()
                hmi.insert_data_in_history_table()

                # Update status labels
                hmi.label_position.setText(f"Posição atual\n{pos}mm")
                hmi.label_inclination.setText(f"Inclinação atual\n{incl}°")

                # Send command to Arduino
                hmi.arduino_comm.send_command([pos, vel, acc, incl, delay])

                # Write to CSV
                if writer:
                    writer.writerow([pos, vel, acc, incl, delay])

        # Ask for observation if CSV was saved
        if save_path and f:
            observation, done = QInputDialog.getText(
                hmi, "Obs", "Insira uma observação (opcional):"
            )
            if done:
                writer.writerow(["Observacao", observation])
            f.close()
