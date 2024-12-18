import sys

from PySide6 import QtCore, QtWidgets

import checksumfile
from verify import verify_checksums, VerificationResult
from verify_window import VerifyRunWindow


class VeepiaciSettings:
    def __init__(self):
        self.checksumFile = ""
        self.directory = ""
        self.resultFile = ""


class VeepiaciMainWindow(QtWidgets.QMainWindow):
    def __init__(self, settings: VeepiaciSettings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle("veepiaci")
        self.thread_pool = QtCore.QThreadPool()

        central_window = QtWidgets.QWidget()
        window_layout = QtWidgets.QGridLayout(central_window)
        self.setCentralWidget(central_window)

        self.checksumFileField = QtWidgets.QLineEdit()
        self.checksumFileField.setText(self.settings.checksumFile)
        self.checksumFileField.setReadOnly(True)
        checksum_file_box = self.create_group_box(
            "Checksum File",
            "This contains the checksums for the files of a directory. Veepiaci can read files in the\nfollowing format: Veepiaci, UltraISO.",
            self.checksumFileField,
            "…",
            self.choose_checksum_file
        )
        window_layout.addWidget(checksum_file_box, 0, 0)

        self.directoryField = QtWidgets.QLineEdit()
        self.directoryField.setText(self.settings.directory)
        self.directoryField.setReadOnly(True)
        directory_box = self.create_group_box(
            "Directory",
            "This directory will have all of its files checked against the checksums contained in the\nchecksum file.",
            self.directoryField,
            "…",
            self.choose_directory
        )
        window_layout.addWidget(directory_box, 1, 0)

        self.verificationResultFileField = QtWidgets.QLineEdit()
        self.verificationResultFileField.setText(self.settings.resultFile)
        self.verificationResultFileField.setReadOnly(True)
        verification_result_file_box = self.create_group_box(
            "Verification Result",
            "The result of the verification run will be stored in this file.",
            self.verificationResultFileField,
            "…",
            self.choose_result_file
        )
        window_layout.addWidget(verification_result_file_box, 2, 0)

        window_layout.setRowStretch(3, 1)

        self.start_verification_button = QtWidgets.QPushButton("Start Verification")
        self.check_if_start_button_can_be_active()
        self.start_verification_button.clicked.connect(self.start_verification)

        button_box = QtWidgets.QWidget()
        button_box_layout = QtWidgets.QHBoxLayout(button_box)
        button_box_layout.addStretch(1)
        button_box_layout.addWidget(self.start_verification_button)
        window_layout.addWidget(button_box, 4, 0)

    @staticmethod
    def create_group_box(title, description, field, button_text, on_click):
        box = QtWidgets.QGroupBox(title)
        label = QtWidgets.QLabel(description)
        label.setWordWrap(False)
        button = QtWidgets.QPushButton(button_text)
        button.clicked.connect(on_click)
        layout = QtWidgets.QGridLayout(box)
        layout.addWidget(label, 0, 0)
        layout.addWidget(field, 1, 0)
        layout.addWidget(button, 1, 1)
        return box

    @QtCore.Slot()
    def choose_checksum_file(self):
        (checksum_file, _) = QtWidgets.QFileDialog.getOpenFileName(self, "Select Checksum File")
        if (checksum_file is not None) and (checksum_file != ""):
            self.set_checksum_file(checksum_file)

    def set_checksum_file(self, checksum_file):
        self.settings.checksumFile = checksum_file
        self.checksumFileField.setText(checksum_file)
        self.check_if_start_button_can_be_active()

    @QtCore.Slot()
    def choose_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self)
        if (directory is not None) and (directory != ""):
            self.set_directory(directory)

    def set_directory(self, directory):
        self.settings.directory = directory
        self.directoryField.setText(directory)
        self.check_if_start_button_can_be_active()

    @QtCore.Slot()
    def choose_result_file(self):
        (result_file, _) = QtWidgets.QFileDialog.getSaveFileName(self, "Select Result File")
        if (result_file is not None) and (result_file != ""):
            self.set_result_file(result_file)

    def set_result_file(self, result_file):
        self.settings.resultFile = result_file
        self.verificationResultFileField.setText(result_file)
        self.check_if_start_button_can_be_active()

    def check_if_start_button_can_be_active(self):
        button_can_be_active = True
        button_can_be_active = button_can_be_active and (self.settings.checksumFile != "")
        button_can_be_active = button_can_be_active and (self.settings.directory != "")
        button_can_be_active = button_can_be_active and (self.settings.resultFile != "")
        self.start_verification_button.setEnabled(button_can_be_active)

    @QtCore.Slot()
    def start_verification(self):
        checksum_file = checksumfile.read_checksum_file(self.settings.checksumFile)

        verify_window = VerifyRunWindow(self)
        verify_window.resize(800, 450)

        worker = VerificationWorker(checksum_file, self.settings.directory)
        worker.started_signal.connect(verify_window.on_started)
        worker.file_hashed_signal.connect(verify_window.on_file_hashed)
        worker.finished_signal.connect(verify_window.on_finished)

        self.thread_pool.start(worker)
        verify_window.exec()


class Mixin(QtCore.QObject):
    started_signal = QtCore.Signal(str)
    file_hashed_signal = QtCore.Signal(str, dict, bool)
    finished_signal = QtCore.Signal(VerificationResult)


class VerificationWorker(QtCore.QRunnable, Mixin):

    def __init__(self, checksum_file, directory):
        super().__init__()

        self.checksum_file = checksum_file
        self.directory = directory

    def run(self):
        verify_checksums(self.checksum_file, self.directory, on_started=self.on_started, on_file_hashed=self.on_file_hashed, on_finished=self.on_finished)

    def on_started(self, directory):
        self.started_signal.emit(directory)

    def on_file_hashed(self, file, hashes, correct):
        self.file_hashed_signal.emit(file, hashes, correct)

    def on_finished(self, verification_result):
        self.finished_signal.emit(verification_result)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    settings = VeepiaciSettings()
    widget = VeepiaciMainWindow(settings)
    widget.resize(widget.layout().minimumSize())
    widget.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
    widget.show()

    sys.exit(app.exec())
