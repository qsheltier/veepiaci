from dataclasses import dataclass
from datetime import datetime

from PySide6 import QtWidgets, QtCore

from verify import VerificationResult


class VerifyRunWindow(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.verification_finished = False
        self.lines = []

        self.setWindowTitle("Verify Checksums")
        self.progress_details = QtWidgets.QTextEdit()
        self.progress_details.setReadOnly(True)
        self.progress_details.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self.progress_details)
        scroll_area.setWidgetResizable(True)

        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.setDisabled(True)
        self.close_button.clicked.connect(self.close)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(scroll_area, 0, 0)
        layout.addWidget(self.close_button, 1, 0, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_W and event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, close_event):
        if not self.verification_finished:
            close_event.ignore()
            return
        super().closeEvent(close_event)

    def add_lines(self, *lines):
        for line in lines:
            self.lines.append(TimestampedLine(line))

    @QtCore.Slot(str)
    def on_started(self, directory):
        self.add_lines("Starting verification in " + directory + "…")
        self.write_lines()

    @QtCore.Slot(str, dict, bool)
    def on_file_hashed(self, file, _, correct_hash):
        self.add_lines(("✅" if correct_hash else "❌") + " " + file)
        self.write_lines()

    @QtCore.Slot(VerificationResult)
    def on_finished(self, verification_result):
        self.add_lines("", "Verification finished. The overall result is: " + ("✅ success" if verification_result.success else "❌ failure"))
        if verification_result.mismatches:
            self.add_lines("", "The following files had incorrect checksums:")
            for mismatch in verification_result.mismatches:
                self.add_lines(mismatch)
        if verification_result.missing_files:
            self.add_lines("", "The following files are missing:")
            for missing_file in verification_result.missing_files:
                self.add_lines(missing_file)
        if verification_result.additional_files:
            self.add_lines("", "The following files did not have checksums:")
            for additional_file in verification_result.additional_files:
                self.add_lines(additional_file)
        self.verification_finished = True
        self.close_button.setEnabled(True)
        self.write_lines()

    def write_lines(self):
        self.progress_details.setText("<html>\n" + "\n".join(map(lambda line: "<div style='line-height: 1.1'>" + line.date.strftime("%Y-%m-%d %H:%M:%S ") + line.text + "</div>", self.lines)) + "</html>")


@dataclass
class TimestampedLine:
    text: str
    date: datetime = datetime.now()