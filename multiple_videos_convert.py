import os
import subprocess
import json # Added for preset management
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtCore import Qt # Added for Qt.Checked
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QComboBox, QLineEdit, QFormLayout, QProgressBar,
    QListWidget, QListWidgetItem, QCheckBox, QHBoxLayout, QGroupBox, QInputDialog # Added QGroupBox, QInputDialog
)

PRESET_FILE = "presets.json"

class VideoConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP4 to OGG & WebM Converter")
        self.setGeometry(100, 100, 500, 450) # Adjusted size for new elements

        # Main Layout
        self.layout = QVBoxLayout()

        # File/Folder Addition Buttons
        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.add_files)
        self.layout.addWidget(self.add_files_button)

        self.add_folder_button = QPushButton("Add Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        self.layout.addWidget(self.add_folder_button)

        # File List Display
        self.file_list_widget = QListWidget()
        self.layout.addWidget(self.file_list_widget)

        # Presets GroupBox
        self.presets_groupbox = QGroupBox("Preset Management")
        self.presets_layout = QVBoxLayout() # Main layout for the groupbox

        self.preset_selection_layout = QHBoxLayout() # Layout for dropdown and delete button
        self.preset_dropdown = QComboBox()
        self.preset_dropdown.setPlaceholderText("<Select a Preset>")
        self.preset_dropdown.activated[str].connect(self.load_selected_preset)
        self.preset_selection_layout.addWidget(QLabel("Preset:"))
        self.preset_selection_layout.addWidget(self.preset_dropdown, 1) # Dropdown takes available space

        self.delete_preset_button = QPushButton("Delete Preset")
        self.delete_preset_button.clicked.connect(self.delete_selected_preset)
        self.delete_preset_button.setEnabled(False) # Initially disabled
        self.preset_selection_layout.addWidget(self.delete_preset_button)
        
        self.presets_layout.addLayout(self.preset_selection_layout)

        self.save_preset_button = QPushButton("Save Current Settings as Preset")
        self.save_preset_button.clicked.connect(self.save_preset_dialog)
        self.presets_layout.addWidget(self.save_preset_button)
        
        self.presets_groupbox.setLayout(self.presets_layout)
        self.layout.addWidget(self.presets_groupbox)


        # Output Quality Controls - now in their own GroupBox for clarity
        self.quality_groupbox = QGroupBox("Output Quality Settings")
        self.form_layout = QFormLayout() # This is the existing form_layout

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
        # self.convert_button.setEnabled(False) # Will be handled by update_convert_button_state
        self.layout.addWidget(self.convert_button)

        # Set Layout
        self.setLayout(self.layout)

        self.quality_groupbox.setLayout(self.form_layout)
        self.layout.addWidget(self.quality_groupbox)

        # Set Layout
        self.setLayout(self.layout)

        # Variables
        self.presets = {} # To store loaded presets
        # self.input_folder = None # Replaced by file_list_widget
        self.output_folder = None # Will be set based on first file or a general setting
        self.files_to_process = [] # To store file paths and their conversion choices
        
        self.load_presets_from_file() # Load presets at startup
        self.update_convert_button_state() # Initial state
        self.update_delete_preset_button_state() # Initial state for delete preset button

    def load_presets_from_file(self):
        """Loads presets from the PRESET_FILE and populates the dropdown."""
        self.preset_dropdown.clear()
        self.preset_dropdown.addItem("<Select a Preset>") # Placeholder first
        self.presets = {}

        try:
            if os.path.exists(PRESET_FILE):
                with open(PRESET_FILE, 'r') as f:
                    self.presets = json.load(f)
                
                if isinstance(self.presets, dict):
                    for preset_name in self.presets.keys():
                        self.preset_dropdown.addItem(preset_name)
                else:
                    # Handle case where JSON is valid but not a dictionary (e.g. a list)
                    print(f"Error: {PRESET_FILE} does not contain a valid preset structure (expected a dictionary).")
                    self.presets = {} # Reset to ensure consistent state
                    # Optionally, inform user via QMessageBox
                    # QMessageBox.warning(self, "Preset Load Error", f"{PRESET_FILE} is corrupted or not a valid preset file.")
            else:
                print(f"{PRESET_FILE} not found. No presets loaded.")
        except FileNotFoundError:
            print(f"{PRESET_FILE} not found. No presets loaded.")
            self.presets = {} # Ensure presets is an empty dict
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {PRESET_FILE}. Presets may be corrupted.")
            self.presets = {} # Ensure presets is an empty dict in case of corruption
            QMessageBox.warning(self, "Preset Load Error", f"Could not load presets from {PRESET_FILE}.\nFile might be corrupted.")
        except Exception as e: # Catch any other unexpected errors during loading
            print(f"An unexpected error occurred while loading presets: {e}")
            self.presets = {}
            QMessageBox.warning(self, "Preset Load Error", f"An unexpected error occurred while loading presets:\n{str(e)}")
            
        self.update_delete_preset_button_state()

    def _get_current_quality_settings(self):
        """Helper to gather current quality settings from UI controls."""
        return {
            "resolution": self.resolution_dropdown.currentText(),
            "audio_bitrate": self.audio_bitrate_dropdown.currentText(),
            "ogg_quality": self.ogg_quality_input.text(),
            "webm_quality": self.webm_quality_input.text(),
            "threads": self.threads_input.text(),
        }

    def save_presets_to_file(self):
        """Saves the current self.presets dictionary to PRESET_FILE."""
        try:
            with open(PRESET_FILE, 'w') as f:
                json.dump(self.presets, f, indent=4)
            print(f"Presets saved to {PRESET_FILE}")
            return True
        except IOError as e:
            print(f"Error saving presets to {PRESET_FILE}: {e}")
            QMessageBox.critical(self, "Save Preset Error", f"Could not save presets to {PRESET_FILE}.\n{str(e)}")
            return False
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred while saving presets: {e}")
            QMessageBox.critical(self, "Save Preset Error", f"An unexpected error occurred while saving presets:\n{str(e)}")
            return False

    def save_preset_dialog(self):
        """Prompts user for a preset name and saves current settings."""
        preset_name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        
        if ok and preset_name: # User clicked OK and entered a name
            current_settings = self._get_current_quality_settings()
            
            self.presets[preset_name] = current_settings
            
            if self.save_presets_to_file():
                # Update dropdown
                if self.preset_dropdown.findText(preset_name) == -1: # Not already in dropdown
                    self.preset_dropdown.addItem(preset_name)
                self.preset_dropdown.setCurrentText(preset_name)
                
                QMessageBox.information(self, "Preset Saved", f"Preset '{preset_name}' saved successfully.")
                self.update_delete_preset_button_state() # A preset is now selected
            # If save_presets_to_file returns False, it already showed an error message
        elif ok and not preset_name: # User clicked OK but name is empty
             QMessageBox.warning(self, "Save Preset Error", "Preset name cannot be empty.")


    def load_selected_preset(self, preset_name):
        # Stub implementation
        if preset_name == "<Select a Preset>":
            self.update_delete_preset_button_state()
            return
        print(f"Stub: load_selected_preset called for {preset_name}")
        # Will load settings from self.presets[preset_name] into UI controls
        QMessageBox.information(self, "Load Preset", f"Load preset '{preset_name}' functionality is not yet implemented.")
        self.update_delete_preset_button_state()

    def delete_selected_preset(self):
        # Stub implementation
        current_preset_name = self.preset_dropdown.currentText()
        if current_preset_name == "<Select a Preset>" or not current_preset_name:
            QMessageBox.warning(self, "Delete Preset", "No preset selected to delete.")
            return
        print(f"Stub: delete_selected_preset called for {current_preset_name}")
        # Will remove preset from self.presets and presets.json, then update dropdown
        QMessageBox.information(self, "Delete Preset", f"Delete preset '{current_preset_name}' functionality is not yet implemented.")
        # After deletion, refresh dropdown and update button state
        # self.load_presets_from_file() # This would reload all
        # Or, more efficiently:
        # if current_preset_name in self.presets: del self.presets[current_preset_name]
        # self.preset_dropdown.removeItem(self.preset_dropdown.findText(current_preset_name))
        # self.save_presets_to_file() # If presets were modified
        self.update_delete_preset_button_state()


    def update_delete_preset_button_state(self):
        """Enable/disable delete preset button based on selection."""
        current_preset = self.preset_dropdown.currentText()
        # Placeholder "<Select a Preset>" should not be deletable
        can_delete = current_preset != "<Select a Preset>" and bool(current_preset)
        self.delete_preset_button.setEnabled(can_delete)


    def add_files(self, test_files=None): # Added test_files for testing
        """Open file dialog to select multiple MP4 files."""
        files_to_add = test_files
        if not files_to_add: # pragma: no cover
            files_to_add, _ = QFileDialog.getOpenFileNames(self, "Select MP4 Files", "", "MP4 Files (*.mp4)")
        
        if files_to_add:
            for file_path in files_to_add:
                if not any(d['path'] == file_path for d in self.files_to_process): # Avoid duplicates
                    self.add_file_to_list(file_path)
            self.update_convert_button_state()

    def add_folder(self, test_folder=None): # Added test_folder for testing
        """Open file dialog to select a folder and add MP4 files from it."""
        folder_to_scan = test_folder
        if not folder_to_scan: # pragma: no cover
            folder_to_scan = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_to_scan:
            for filename in os.listdir(folder_to_scan):
                if filename.lower().endswith(".mp4"):
                    file_path = os.path.join(folder_to_scan, filename)
                    if not any(d['path'] == file_path for d in self.files_to_process): # Avoid duplicates
                        self.add_file_to_list(file_path)
            self.update_convert_button_state()

    def add_file_to_list(self, file_path):
        """Adds a file to the list widget with custom controls and stores its data."""
        item_data = {'path': file_path, 'convert_ogg': True, 'convert_webm': True}
        self.files_to_process.append(item_data)

        list_item = QListWidgetItem(self.file_list_widget)
        
        custom_widget = QWidget()
        custom_layout = QHBoxLayout(custom_widget)
        custom_layout.setContentsMargins(5, 2, 5, 2) # Adjust margins for tighter packing

        file_label = QLabel(os.path.basename(file_path)) # Show only filename
        file_label.setToolTip(file_path) # Show full path on hover

        ogg_checkbox = QCheckBox("OGG")
        ogg_checkbox.setChecked(True)
        ogg_checkbox.stateChanged.connect(lambda state, path=file_path: self.update_conversion_choice(path, 'ogg', state))

        webm_checkbox = QCheckBox("WebM")
        webm_checkbox.setChecked(True)
        webm_checkbox.stateChanged.connect(lambda state, path=file_path: self.update_conversion_choice(path, 'webm', state))
        
        custom_layout.addWidget(file_label, 1) # Add label with stretch factor
        custom_layout.addWidget(ogg_checkbox)
        custom_layout.addWidget(webm_checkbox)
        
        custom_widget.setLayout(custom_layout)
        list_item.setSizeHint(custom_widget.sizeHint())
        
        self.file_list_widget.addItem(list_item)
        self.file_list_widget.setItemWidget(list_item, custom_widget)

    def update_conversion_choice(self, file_path, format_type, state):
        """Updates the conversion choice for a file in self.files_to_process."""
        for item_data in self.files_to_process:
            if item_data['path'] == file_path:
                if format_type == 'ogg':
                    item_data['convert_ogg'] = (state == Qt.Checked)
                elif format_type == 'webm':
                    item_data['convert_webm'] = (state == Qt.Checked)
                break
        # For debugging, print the updated list
        # print(self.files_to_process)

    def update_convert_button_state(self):
        """Enable/disable convert button based on file list."""
        self.convert_button.setEnabled(len(self.files_to_process) > 0)


    def convert_videos(self):
        """Convert selected MP4 videos to OGG and/or WebM based on per-file choices."""
        if not self.files_to_process:
            QMessageBox.warning(self, "Warning", "Please add files to convert first!")
            return

        # Filter files that actually need conversion
        files_to_convert_tasks = [
            item_data for item_data in self.files_to_process
            if item_data.get('convert_ogg', False) or item_data.get('convert_webm', False)
        ]

        if not files_to_convert_tasks:
            QMessageBox.information(self, "No Conversions Selected", "No files have OGG or WebM formats selected for conversion.")
            return

        # Global FFmpeg options from UI
        resolution = self.get_resolution()
        audio_bitrate = self.get_audio_bitrate()
        threads_per_ffmpeg_process = self.get_threads() # Renamed for clarity
        ogg_quality = self.get_ogg_quality()
        webm_quality = self.get_webm_quality()

        # Progress Bar setup
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(files_to_convert_tasks))

        # Determine number of parallel worker threads for the ThreadPoolExecutor
        # This is different from threads_per_ffmpeg_process.
        # For simplicity, let's use a fixed number of worker threads or make it configurable if needed.
        # Here, using the same "FFmpeg Threads" input for ThreadPoolExecutor workers for now.
        try:
            # This 'threads' variable is for the ThreadPoolExecutor max_workers
            num_worker_threads = max(1, int(self.threads_input.text())) 
        except ValueError:
            num_worker_threads = 4  # Default worker threads for ThreadPoolExecutor

        completed_count = 0
        successful_ogg_conversions = 0
        successful_webm_conversions = 0
        files_with_errors = 0
        error_details = [] # Store more detailed error messages

        with ThreadPoolExecutor(max_workers=num_worker_threads) as executor:
            futures = {
                executor.submit(
                    self.convert_video,
                    item_data['path'],
                    item_data['convert_ogg'],
                    item_data['convert_webm'],
                    resolution,
                    audio_bitrate,
                    ogg_quality,
                    webm_quality,
                    threads_per_ffmpeg_process # This is the -threads for ffmpeg command
                ): item_data['path'] for item_data in files_to_convert_tasks
            }

            for future in as_completed(futures):
                original_file_path = futures[future]
                try:
                    result = future.result()  # result is a dict from convert_video
                    
                    if result['status'] == "success":
                        if "OGG" in result['formats']:
                            successful_ogg_conversions += 1
                        if "WebM" in result['formats']:
                            successful_webm_conversions += 1
                    elif result['status'] == "error":
                        files_with_errors +=1
                        for err_msg in result['errors']:
                            error_details.append(f"File {os.path.basename(original_file_path)}: {err_msg}")
                    # Other statuses like "skipped" or "noop" are logged by convert_video itself.
                
                except Exception as e:
                    # This catches errors from the future.result() call itself, or unexpected issues in convert_video
                    files_with_errors +=1
                    err_msg = f"Critical error processing {os.path.basename(original_file_path)}: {str(e)}"
                    print(err_msg) # Log critical errors to console
                    error_details.append(err_msg)
                
                completed_count += 1
                self.progress_bar.setValue(completed_count)

        # Report results
        total_files_processed = len(files_to_convert_tasks)
        summary_message = f"Conversion process finished.\n\n"
        summary_message += f"Total files attempted: {total_files_processed}\n"
        summary_message += f"Successfully converted to OGG: {successful_ogg_conversions} file(s)\n"
        summary_message += f"Successfully converted to WebM: {successful_webm_conversions} file(s)\n"
        
        if files_with_errors > 0:
            summary_message += f"\nEncountered errors with {files_with_errors} file(s).\n"
            # Show first few errors in message box
            for i, err in enumerate(error_details[:3]): # Show up to 3 detailed errors
                summary_message += f"- {err}\n"
            if len(error_details) > 3:
                summary_message += f"- ... (see console for {len(error_details) - 3} more details)\n"
        
        if not error_details and files_with_errors > 0: # Generic error message if details are missing for some reason
            summary_message += f"Some files had conversion errors. Please check console logs.\n"

        if total_files_processed == 0 and len(self.files_to_process) > 0: # All files were deselected
             summary_message = "No files were selected for OGG or WebM conversion."


        print("\n--- Conversion Summary ---")
        print(f"Total files attempted: {total_files_processed}")
        print(f"Successful OGG conversions: {successful_ogg_conversions}")
        print(f"Successful WebM conversions: {successful_webm_conversions}")
        print(f"Files with errors: {files_with_errors}")
        if error_details:
            print("Error Details:")
            for err in error_details:
                print(f"  - {err}")
        print("--- End of Summary ---\n")
        
        QMessageBox.information(self, "Conversion Complete", summary_message)

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

    def convert_video(self, file_path, convert_to_ogg, convert_to_webm, resolution, audio_bitrate, ogg_quality, webm_quality, threads):
        """Convert a single MP4 video to OGG and/or WebM based on flags."""
        filename = os.path.basename(file_path)
        base_output_folder = os.path.join(os.path.dirname(file_path), "converted")
        os.makedirs(base_output_folder, exist_ok=True)

        converted_formats = []
        errors = []

        if convert_to_ogg:
            try:
                ogg_output_file = os.path.join(base_output_folder, os.path.splitext(filename)[0] + ".ogg")
                print(f"Converting {filename} to OGG...")
                ffmpeg_command = [
                    "ffmpeg", "-y", "-i", file_path,
                    "-c:v", "libtheora",
                    "-c:a", "libvorbis",
                    "-q:v", str(ogg_quality),
                    "-q:a", "5", # Audio quality for OGG (fixed at medium)
                    "-threads", str(threads),
                    ogg_output_file
                ]
                if resolution:
                    ffmpeg_command.insert(-2, "-vf")
                    ffmpeg_command.insert(-2, resolution)
                if audio_bitrate:
                    ffmpeg_command.insert(-2, "-b:a")
                    ffmpeg_command.insert(-2, audio_bitrate)
                
                subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
                print(f"Successfully converted {filename} to OGG.")
                converted_formats.append("OGG")
            except subprocess.CalledProcessError as e:
                error_message = f"Failed to convert {filename} to OGG: {e.stderr}"
                print(error_message)
                errors.append(error_message)
            except Exception as e: # Catch other potential errors
                error_message = f"An unexpected error occurred while converting {filename} to OGG: {str(e)}"
                print(error_message)
                errors.append(error_message)


        if convert_to_webm:
            try:
                webm_output_file = os.path.join(base_output_folder, os.path.splitext(filename)[0] + ".webm")
                print(f"Converting {filename} to WebM...")
                ffmpeg_command = [
                    "ffmpeg", "-y", "-i", file_path,
                    "-c:v", "libvpx-vp9",
                    "-c:a", "libopus",
                    "-crf", str(webm_quality),
                    "-threads", str(threads),
                    webm_output_file
                ]
                if resolution:
                    ffmpeg_command.insert(-2, "-vf")
                    ffmpeg_command.insert(-2, resolution)
                if audio_bitrate:
                    ffmpeg_command.insert(-2, "-b:a")
                    ffmpeg_command.insert(-2, audio_bitrate)

                subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
                print(f"Successfully converted {filename} to WebM.")
                converted_formats.append("WebM")
            except subprocess.CalledProcessError as e:
                error_message = f"Failed to convert {filename} to WebM: {e.stderr}"
                print(error_message)
                errors.append(error_message)
            except Exception as e: # Catch other potential errors
                error_message = f"An unexpected error occurred while converting {filename} to WebM: {str(e)}"
                print(error_message)
                errors.append(error_message)

        if not convert_to_ogg and not convert_to_webm:
            print(f"No conversion selected for {filename}.")
            return {"path": file_path, "status": "skipped", "formats": [], "errors": []}


        if errors:
            # If there were errors, the status reflects that, even if one format succeeded
            return {"path": file_path, "status": "error", "formats": converted_formats, "errors": errors}
        elif converted_formats:
            # If at least one format converted successfully and no errors
            return {"path": file_path, "status": "success", "formats": converted_formats, "errors": []}
        else:
            # Should not be reached if at least one format was selected, but as a fallback
            return {"path": file_path, "status": "noop", "formats": [], "errors": ["No conversion attempted or an unknown issue."]}


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = VideoConverterApp()
    window.show()
    app.exec()
