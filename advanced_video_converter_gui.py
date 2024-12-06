import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox, QLineEdit, QFormLayout, QProgressBar
)

class VideoConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP4 to OGG & WebM Converter")
        self.setGeometry(100, 100, 400, 350)

        # Main Layout
        self.layout = QVBoxLayout()

        # Folder Selection
        self.label = QLabel("Select a folder containing MP4 videos to convert:")
        self.layout.addWidget(self.label)
        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_button)

        # Output Quality Controls
        self.form_layout = QFormLayout()

        # Video Resolution
        self.resolution_dropdown = QComboBox()
        self.resolution_dropdown.addItems(["480p", "720p", "1080p", "Original"])
        self.form_layout.addRow("Video Resolution:", self.resolution_dropdown)

        # Audio Bitrate
        self.audio_bitrate_dropdown = QComboBox()
        self.audio_bitrate_dropdown.addItems(["64k", "128k", "192k", "Original"])
        self.form_layout.addRow("Audio Bitrate:", self.audio_bitrate_dropdown)

        # OGG Video Quality
        self.ogg_quality_input = QLineEdit()
        self.ogg_quality_input.setText("5")  # Default OGG quality
        self.form_layout.addRow("OGG Video Quality (1-10):", self.ogg_quality_input)

        # WebM Video Quality
        self.webm_quality_input = QLineEdit()
        self.webm_quality_input.setText("30")  # Default WebM quality
        self.form_layout.addRow("WebM CRF (Lower = Better):", self.webm_quality_input)

        # Threads
        self.threads_input = QLineEdit()
        self.threads_input.setText("4")  # Default number of threads
        self.form_layout.addRow("FFmpeg Threads:", self.threads_input)

        self.layout.addLayout(self.form_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Convert Button
        self.convert_button = QPushButton("Convert Videos")
        self.convert_button.clicked.connect(self.convert_videos)
        self.convert_button.setEnabled(False)
        self.layout.addWidget(self.convert_button)

        # Set Layout
        self.setLayout(self.layout)

        # Variables
        self.input_folder = None
        self.output_folder = None

    def select_folder(self):
        """Open file dialog to select an input folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.input_folder = folder
            self.output_folder = os.path.join(folder, "converted")
            self.label.setText(f"Selected Folder: {folder}")
            self.convert_button.setEnabled(True)

    def convert_videos(self):
        """Convert MP4 videos to OGG and WebM in parallel."""
        if not self.input_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first!")
            return

        # Ensure output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

        # Gather FFmpeg options from UI
        resolution = self.get_resolution()
        audio_bitrate = self.get_audio_bitrate()
        threads = self.get_threads()
        ogg_quality = self.get_ogg_quality()
        webm_quality = self.get_webm_quality()

        supported_extensions = {".mp4"}
        files_to_convert = [
            os.path.join(self.input_folder, filename)
            for filename in os.listdir(self.input_folder)
            if os.path.splitext(filename)[1].lower() in supported_extensions
        ]

        if not files_to_convert:
            QMessageBox.information(self, "No Videos Found", "No MP4 files found in the selected folder.")
            return

        # Reset Progress Bar
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(files_to_convert))

        # Use ThreadPoolExecutor for parallel processing
        max_workers = min(threads, len(files_to_convert))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.convert_video, file_path, resolution, audio_bitrate, ogg_quality, webm_quality, threads): file_path
                for file_path in files_to_convert
            }

            completed_count = 0
            for future in as_completed(futures):
                try:
                    future.result()
                    completed_count += 1
                    self.progress_bar.setValue(completed_count)  # Update progress bar
                except Exception as e:
                    print(f"Error converting {futures[future]}: {e}")

        QMessageBox.information(self, "Conversion Complete", f"Successfully converted {completed_count} videos.\nSaved to: {self.output_folder}")

    def get_resolution(self):
        """Map resolution dropdown to FFmpeg scale."""
        resolution = self.resolution_dropdown.currentText()
        if resolution == "480p":
            return "scale=-2:480"
        elif resolution == "720p":
            return "scale=-2:720"
        elif resolution == "1080p":
            return "scale=-2:1080"
        return None  # Original resolution

    def get_audio_bitrate(self):
        """Get audio bitrate from dropdown."""
        bitrate = self.audio_bitrate_dropdown.currentText()
        return None if bitrate == "Original" else bitrate

    def get_ogg_quality(self):
        """Get OGG video quality (1-10)."""
        try:
            return max(1, min(10, int(self.ogg_quality_input.text())))
        except ValueError:
            return 5  # Default OGG quality

    def get_webm_quality(self):
        """Get WebM CRF value."""
        try:
            return max(0, int(self.webm_quality_input.text()))
        except ValueError:
            return 30  # Default WebM quality

    def get_threads(self):
        """Get number of threads from input."""
        try:
            return max(1, int(self.threads_input.text()))
        except ValueError:
            return 4  # Default to 4 threads

    def convert_video(self, file_path, resolution, audio_bitrate, ogg_quality, webm_quality, threads):
        """Convert a single MP4 video to OGG and WebM."""
        filename = os.path.basename(file_path)
        try:
            # OGG Output
            ogg_output_file = os.path.join(self.output_folder, os.path.splitext(filename)[0] + ".ogg")
            print(f"Converting {filename} to OGG...")
            ffmpeg_command = [
                "ffmpeg", "-y", "-i", file_path,
                "-c:v", "libtheora",  # Video codec for OGG
                "-c:a", "libvorbis",  # Audio codec for OGG
                "-q:v", str(ogg_quality),  # Video quality for OGG
                "-q:a", "5",          # Audio quality for OGG (fixed at medium)
                f"-threads", str(threads),
                ogg_output_file
            ]
            if resolution:
                ffmpeg_command.insert(-2, "-vf")
                ffmpeg_command.insert(-2, resolution)
            if audio_bitrate:
                ffmpeg_command.insert(-2, "-b:a")
                ffmpeg_command.insert(-2, audio_bitrate)

            subprocess.run(ffmpeg_command, check=True)

            # WebM Output
            webm_output_file = os.path.join(self.output_folder, os.path.splitext(filename)[0] + ".webm")
            print(f"Converting {filename} to WebM...")
            ffmpeg_command = [
                "ffmpeg", "-y", "-i", file_path,
                "-c:v", "libvpx-vp9",  # Video codec for WebM
                "-c:a", "libopus",     # Audio codec for WebM
                "-crf", str(webm_quality),  # Video quality for WebM
                f"-threads", str(threads),
                webm_output_file
            ]
            if resolution:
                ffmpeg_command.insert(-2, "-vf")
                ffmpeg_command.insert(-2, resolution)
            if audio_bitrate:
                ffmpeg_command.insert(-2, "-b:a")
                ffmpeg_command.insert(-2, audio_bitrate)

            subprocess.run(ffmpeg_command, check=True)

            print(f"Converted {filename} to OGG and WebM.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {filename}: {e}")
            raise e

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = VideoConverterApp()
    window.show()
    app.exec()
