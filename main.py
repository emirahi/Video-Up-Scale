import subprocess
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QLabel, QWidget, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal

class VideoProcessingThread(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, input_file, output_file):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        try:
            # Simulate process progress
            command = [
                "ffmpeg",
                "-i", self.input_file,                # Input file
                "-vf", "scale=2560:1440",        # Scaling filter to 1440p
                "-r", "60",                     # Set frame rate to 60 FPS
                "-c:v", "libx264",              # Video codec
                "-crf", "23",                   # Constant Rate Factor for quality
                "-preset", "medium",            # Encoding speed
                "-c:a", "aac",                  # Audio codec
                "-b:a", "192k",                 # Audio bitrate
                self.output_file                   # Output file
            ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")

            for line in process.stdout:
                if "frame=" in line:
                    # Simulate progress update (not exact but gives user feedback)
                    self.progress.emit(50)  # Example: Emit progress

            process.communicate()

            if process.returncode == 0:
                self.progress.emit(100)
                self.completed.emit(f"Video successfully upscaled and saved to: {self.output_file}")
            else:
                self.failed.emit("Error during video processing. Please check the input file and try again.")

        except Exception as e:
            self.failed.emit(f"An unexpected error occurred: {str(e)}")


class VideoUpscalerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Upscaler - 1080p to 1440p")
        self.setGeometry(200, 200, 400, 250)

        # Main layout
        self.layout = QVBoxLayout()

        # Label to show selected file
        self.file_label = QLabel("No file selected")
        self.layout.addWidget(self.file_label)

        # Button to select input file
        self.select_button = QPushButton("Select Video File")
        self.select_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_button)

        # Button to upscale video
        self.upscale_button = QPushButton("Upscale Video")
        self.upscale_button.clicked.connect(self.upscale_video)
        self.upscale_button.setEnabled(False)
        self.layout.addWidget(self.upscale_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Status: Idle")
        self.layout.addWidget(self.status_label)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Variables
        self.input_file = ""
        self.thread = None

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.mkv *.avi)")
        if file_path:
            self.input_file = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.upscale_button.setEnabled(True)

    def upscale_video(self):
        if not self.input_file:
            self.file_label.setText("No file selected")
            return

        output_file = QFileDialog.getSaveFileName(self, "Save Upscaled Video", "output_video_1440p.mp4", "Video Files (*.mp4)")[0]
        if not output_file:
            return

        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Processing...")

        self.thread = VideoProcessingThread(self.input_file, output_file)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.completed.connect(self.on_processing_complete)
        self.thread.failed.connect(self.on_processing_failed)

        self.thread.start()

    def on_processing_complete(self, message):
        self.status_label.setText("Status: Completed")
        self.file_label.setText(message)
        self.progress_bar.setValue(100)

    def on_processing_failed(self, message):
        self.status_label.setText("Status: Failed")
        self.file_label.setText(message)
        self.progress_bar.setValue(0)


if __name__ == "__main__":
    app = QApplication([])
    window = VideoUpscalerApp()
    window.show()
    app.exec_()
