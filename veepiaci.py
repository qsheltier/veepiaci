import sys

from PySide6 import QtCore, QtWidgets

import checksumfile
from verify import verify_checksums


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

        worker = VerificationWorker(checksum_file, self.settings.directory, verify_window.on_file_hashed, verify_window.on_finished)
        self.thread_pool.start(worker)

        verify_window.exec()


class VerificationWorker(QtCore.QRunnable):

    def __init__(self, checksum_file, directory, on_file_hashed, on_finished):
        super().__init__()
        self.checksum_file = checksum_file
        self.directory = directory
        self.on_file_hashed = on_file_hashed
        self.on_finished = on_finished

    def run(self):
        verify_checksums(self.checksum_file, self.directory, self.on_file_hashed, self.on_finished)


class VerifyRunWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.verification_finished = False

        self.setWindowTitle("Verify Checksums")
        self.progress_details = QtWidgets.QLabel()
        self.progress_details.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self.progress_details)
        scroll_area.setWidgetResizable(True)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(scroll_area, 0, 0)
        self.setLayout(layout)

    def closeEvent(self, close_event):
        if not self.verification_finished:
            close_event.ignore()
            return
        super().closeEvent(close_event)

    def on_file_hashed(self, file, _, correct_hash):
        self.progress_details.setText(self.progress_details.text() + ("✅" if correct_hash else "❌") + " " + file + "\n")

    def on_finished(self, verification_result):
        text = self.progress_details.text()
        text += "\n"
        text += "Verification finished. The overall result is: " + ("✅ success" if verification_result.success else "❌ failure") + "\n"
        if verification_result.mismatches:
            text += "\nThe following files had incorrect checksums:\n"
            for mismatch in verification_result.mismatches:
                text += mismatch + "\n"
        if verification_result.missing_files:
            text += "\nThe following files are missing:\n"
            for missing_file in verification_result.missing_files:
                text += missing_file + "\n"
        if verification_result.additional_files:
            text += "\nThe following files did not have checksums:\n"
            for additional_file in verification_result.additional_files:
                text += additional_file + "\n"
        self.progress_details.setText(text)
        self.verification_finished = True


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    settings = VeepiaciSettings()
    widget = VeepiaciMainWindow(settings)
    widget.resize(widget.layout().minimumSize())
    widget.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
    widget.show()

    sys.exit(app.exec())
