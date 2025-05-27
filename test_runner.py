import os
import sys
import shutil # For cleaning up test files/dirs
from unittest.mock import MagicMock # MagicMock can be used if specific assertions on call counts etc. are needed later

# Attempt to ensure system PyQt5 modules are found
sys.path.insert(0, "/usr/lib/python3/dist-packages")
sys.path.insert(0, "/app") # Add the app directory as well

# --- MockQMessageBox Class (same as before) ---
class MockQMessageBox:
    # Keep track of calls - class level
    calls = []

    def __init__(self, parent=None):
        self.parent = parent
        self.icon = None
        self.text = ""
        self.informative_text = ""
        self.standard_buttons = None
        self.detailed_text = ""
        # Record the call to __init__ if needed, but static/class methods are more common for QMessageBox
        # MockQMessageBox.calls.append({'type': 'init', 'parent': parent}) 

    def setIcon(self, icon):
        self.icon = icon
    def setText(self, text):
        self.text = text
    def setInformativeText(self, text):
        self.informative_text = text
    def setStandardButtons(self, buttons):
        self.standard_buttons = buttons
    def setDetailedText(self, text):
        self.detailed_text = text
    
    def exec_(self): # For older PyQt versions, exec_ might be used
        call_info = {
            'type': 'exec_', 'icon': self.icon, 'text': self.text, 
            'informative_text': self.informative_text, 'instance': self
        }
        MockQMessageBox.calls.append(call_info)
        print(f"MockQMessageBox.exec_ called: Text='{self.text}'")
        return True # Simulate a button press

    def exec(self): # For newer PyQt, exec is used
        call_info = {
            'type': 'exec', 'icon': self.icon, 'text': self.text, 
            'informative_text': self.informative_text, 'instance': self
        }
        MockQMessageBox.calls.append(call_info)
        print(f"MockQMessageBox.exec called: Text='{self.text}'")
        return True

    @staticmethod
    def information(parent, title, message):
        print(f"MockQMessageBox.information: Title='{title}', Message='{message}'")
        MockQMessageBox.calls.append({
            'type': 'information', 'parent': parent, 'title': title, 'message': message
        })
        return True 

    @staticmethod
    def warning(parent, title, message):
        print(f"MockQMessageBox.warning: Title='{title}', Message='{message}'")
        MockQMessageBox.calls.append({
            'type': 'warning', 'parent': parent, 'title': title, 'message': message
        })
        return True

    @staticmethod
    def critical(parent, title, message):
        print(f"MockQMessageBox.critical: Title='{title}', Message='{message}'")
        MockQMessageBox.calls.append({
            'type': 'critical', 'parent': parent, 'title': title, 'message': message
        })
        return True
    
    @classmethod
    def reset_calls(cls):
        cls.calls = []

# Import the module that uses QMessageBox FIRST
import multiple_videos_convert

# NOW, monkey-patch QMessageBox directly in the imported module's namespace
multiple_videos_convert.QMessageBox = MockQMessageBox

# Now import the specific classes needed from the module
from multiple_videos_convert import VideoConverterApp, QApplication


# --- Test Helper Functions ---
def get_abs_path(relative_path):
    # Ensure paths are constructed from /app, which is the repo root in the sandbox
    return os.path.join("/app", relative_path)

def setup_test_environment():
    print("Setting up test environment...")
    os.makedirs(get_abs_path("test_files/dir1"), exist_ok=True)
    os.makedirs(get_abs_path("test_files/dir2"), exist_ok=True)
    with open(get_abs_path("test_files/dir1/test_video1.mp4"), "w") as f:
        f.write("This is dummy MP4 content for video 1.")
    with open(get_abs_path("test_files/dir1/test_video2.mp4"), "w") as f:
        f.write("This is dummy MP4 content for video 2.")
    with open(get_abs_path("test_files/dir2/test_video3.mp4"), "w") as f:
        f.write("This is dummy MP4 content for video 3.")
    print("Test environment setup complete.")

def cleanup_test_environment():
    print("Cleaning up test environment...")
    # Clean up 'converted' directories first
    dir1_converted = get_abs_path("test_files/dir1/converted")
    if os.path.exists(dir1_converted):
        shutil.rmtree(dir1_converted)
    dir2_converted = get_abs_path("test_files/dir2/converted")
    if os.path.exists(dir2_converted):
        shutil.rmtree(dir2_converted)
    # Then remove the main test_files directory
    if os.path.exists(get_abs_path("test_files")):
        shutil.rmtree(get_abs_path("test_files"))
    print("Test environment cleanup complete.")

def print_test_result(test_name, passed, details=""):
    status = "PASSED" if passed else "FAILED"
    print(f"Test: {test_name} - {status}")
    if details:
        print(f"  Details: {details}")
    print("-" * 30)

# --- Test Cases ---

def test_case_1_ui_interaction_file_addition(app_window):
    test_name = "Test Case 1: UI Interaction & File Addition"
    print(f"\n--- Running {test_name} ---")
    MockQMessageBox.reset_calls()
    app_window.files_to_process = [] # Reset file list
    app_window.file_list_widget.clear() # Clear UI list
    app_window.update_convert_button_state()

    initial_button_state = app_window.convert_button.isEnabled()
    print_test_result(f"{test_name} - Initial Convert Button Disabled", not initial_button_state, f"Button state: {initial_button_state}")

    video1_path = get_abs_path("test_files/dir1/test_video1.mp4")
    video2_path = get_abs_path("test_files/dir1/test_video2.mp4")
    app_window.add_files(test_files=[video1_path, video2_path])
    
    passed_add_files = len(app_window.files_to_process) == 2 and \
                       app_window.files_to_process[0]['path'] == video1_path and \
                       app_window.files_to_process[1]['path'] == video2_path and \
                       app_window.files_to_process[0]['convert_ogg'] and app_window.files_to_process[0]['convert_webm'] and \
                       app_window.files_to_process[1]['convert_ogg'] and app_window.files_to_process[1]['convert_webm']
    print_test_result(f"{test_name} - Add Files (video1, video2)", passed_add_files, f"Files in list: {len(app_window.files_to_process)}")

    button_state_after_add = app_window.convert_button.isEnabled()
    print_test_result(f"{test_name} - Convert Button Enabled After Add", button_state_after_add, f"Button state: {button_state_after_add}")

    dir1_path = get_abs_path("test_files/dir1")
    app_window.add_folder(test_folder=dir1_path)
    passed_add_folder_no_dupes = len(app_window.files_to_process) == 2
    print_test_result(f"{test_name} - Add Folder (dir1, no duplicates)", passed_add_folder_no_dupes, f"Files in list: {len(app_window.files_to_process)}")

    video3_path = get_abs_path("test_files/dir2/test_video3.mp4")
    dir2_path = get_abs_path("test_files/dir2")
    app_window.add_folder(test_folder=dir2_path)
    passed_add_folder_video3 = len(app_window.files_to_process) == 3 and \
                               any(f['path'] == video3_path for f in app_window.files_to_process)
    print_test_result(f"{test_name} - Add Folder (dir2, adds video3)", passed_add_folder_video3, f"Files in list: {len(app_window.files_to_process)}")
    
    app_window.files_to_process = []
    app_window.file_list_widget.clear()
    app_window.update_convert_button_state()
    final_button_state = app_window.convert_button.isEnabled()
    print_test_result(f"{test_name} - Convert Button Disabled After Clear", not final_button_state, f"Button state: {final_button_state}")


def test_case_2_format_selection_conversion(app_window):
    test_name = "Test Case 2: Format Selection & Conversion Logic"
    print(f"\n--- Running {test_name} ---")
    
    video1_path = get_abs_path("test_files/dir1/test_video1.mp4")
    video2_path = get_abs_path("test_files/dir1/test_video2.mp4")
    video3_path = get_abs_path("test_files/dir2/test_video3.mp4")

    # Scenario 1: video1 (OGG only), video2 (WebM only)
    print("\n  Scenario 1: video1 (OGG only), video2 (WebM only)")
    MockQMessageBox.reset_calls()
    cleanup_test_environment() 
    setup_test_environment() 
    app_window.files_to_process = []
    app_window.file_list_widget.clear()
    app_window.add_files(test_files=[video1_path, video2_path])
    app_window.update_conversion_choice(video1_path, 'webm', False) 
    app_window.update_conversion_choice(video2_path, 'ogg', False) 
    
    print(f"  Pre-conversion files_to_process for Scenario 1: {app_window.files_to_process}")
    app_window.convert_videos()

    video1_ogg_exists = os.path.exists(get_abs_path("test_files/dir1/converted/test_video1.ogg"))
    video1_webm_exists = os.path.exists(get_abs_path("test_files/dir1/converted/test_video1.webm"))
    video2_ogg_exists = os.path.exists(get_abs_path("test_files/dir1/converted/test_video2.ogg"))
    video2_webm_exists = os.path.exists(get_abs_path("test_files/dir1/converted/test_video2.webm"))

    passed_scenario1 = video1_ogg_exists and not video1_webm_exists and \
                       not video2_ogg_exists and video2_webm_exists
    details_s1 = f"video1.ogg: {video1_ogg_exists}, video1.webm: {video1_webm_exists}, video2.ogg: {video2_ogg_exists}, video2.webm: {video2_webm_exists}"
    print_test_result(f"{test_name} - Scenario 1 Conversion", passed_scenario1, details_s1)
    
    last_msg_s1 = MockQMessageBox.calls[-1] if MockQMessageBox.calls else {}
    print(f"  QMessageBox for Scenario 1: Title='{last_msg_s1.get('title')}', Message='{last_msg_s1.get('message')}'")


    # Scenario 2: video1 (Both), video2 (Neither)
    print("\n  Scenario 2: video1 (Both OGG & WebM), video2 (Neither)")
    MockQMessageBox.reset_calls()
    cleanup_test_environment() 
    setup_test_environment()   
    app_window.files_to_process = []
    app_window.file_list_widget.clear()
    app_window.add_files(test_files=[video1_path, video2_path])
    app_window.update_conversion_choice(video2_path, 'ogg', False)
    app_window.update_conversion_choice(video2_path, 'webm', False)
    
    print(f"  Pre-conversion files_to_process for Scenario 2: {app_window.files_to_process}")
    app_window.convert_videos()

    video1_ogg_exists_s2 = os.path.exists(get_abs_path("test_files/dir1/converted/test_video1.ogg"))
    video1_webm_exists_s2 = os.path.exists(get_abs_path("test_files/dir1/converted/test_video1.webm"))
    video2_ogg_exists_s2 = os.path.exists(get_abs_path("test_files/dir1/converted/test_video2.ogg"))
    video2_webm_exists_s2 = os.path.exists(get_abs_path("test_files/dir1/converted/test_video2.webm"))

    # For Scenario 2, progress bar should be max 1 (only video1 is processed)
    # This requires checking the state of progress_bar within convert_videos or its setup
    # For now, focusing on file output and reported messages
    
    passed_scenario2 = video1_ogg_exists_s2 and video1_webm_exists_s2 and \
                       not video2_ogg_exists_s2 and not video2_webm_exists_s2
    details_s2 = f"video1.ogg: {video1_ogg_exists_s2}, video1.webm: {video1_webm_exists_s2}, video2.ogg: {video2_ogg_exists_s2}, video2.webm: {video2_webm_exists_s2}"
    print_test_result(f"{test_name} - Scenario 2 Conversion", passed_scenario2, details_s2)
    last_msg_s2 = MockQMessageBox.calls[-1] if MockQMessageBox.calls else {}
    print(f"  QMessageBox for Scenario 2: Title='{last_msg_s2.get('title')}', Message='{last_msg_s2.get('message')}'")
    # Check if message indicates only 1 file processed if video2 was skipped
    if last_msg_s2.get('title') == "Conversion Complete":
        assert "Total files attempted: 1" in last_msg_s2.get('message'), "Scenario 2 should report 1 file attempted for conversion"


    # Scenario 3: video3 (OGG only) from different directory
    print("\n  Scenario 3: video3 (OGG only) from dir2")
    MockQMessageBox.reset_calls()
    # cleanup_test_environment() # dir1/converted might still exist, but we are testing dir2
    # setup_test_environment()  # Ensure dir2/test_video3.mp4 is there
    if not os.path.exists(get_abs_path("test_files/dir2/test_video3.mp4")): # Ensure file exists if not cleaning everything
        os.makedirs(get_abs_path("test_files/dir2"), exist_ok=True)
        with open(get_abs_path("test_files/dir2/test_video3.mp4"), "w") as f:
            f.write("This is dummy MP4 content for video 3.")

    app_window.files_to_process = [] 
    app_window.file_list_widget.clear()
    app_window.add_files(test_files=[video3_path])
    app_window.update_conversion_choice(video3_path, 'webm', False)
    
    print(f"  Pre-conversion files_to_process for Scenario 3: {app_window.files_to_process}")
    app_window.convert_videos()

    video3_ogg_exists_s3 = os.path.exists(get_abs_path("test_files/dir2/converted/test_video3.ogg"))
    video3_webm_exists_s3 = os.path.exists(get_abs_path("test_files/dir2/converted/test_video3.webm"))
    
    passed_scenario3 = video3_ogg_exists_s3 and not video3_webm_exists_s3
    details_s3 = f"video3.ogg: {video3_ogg_exists_s3}, video3.webm: {video3_webm_exists_s3}"
    print_test_result(f"{test_name} - Scenario 3 Conversion", passed_scenario3, details_s3)
    last_msg_s3 = MockQMessageBox.calls[-1] if MockQMessageBox.calls else {}
    print(f"  QMessageBox for Scenario 3: Title='{last_msg_s3.get('title')}', Message='{last_msg_s3.get('message')}'")


def test_case_3_output_reporting(app_window):
    test_name = "Test Case 3: Output & Reporting (using dummy files)"
    print(f"\n--- Running {test_name} ---")
    MockQMessageBox.reset_calls()
    cleanup_test_environment() 
    setup_test_environment()   

    video1_path = get_abs_path("test_files/dir1/test_video1.mp4")
    app_window.files_to_process = []
    app_window.file_list_widget.clear()
    app_window.add_files(test_files=[video1_path])
    # video1 has OGG=True, WebM=True by default
    
    print(f"  Pre-conversion files_to_process for Reporting Test: {app_window.files_to_process}")
    app_window.convert_videos() 
    
    reported_correctly = False
    if MockQMessageBox.calls:
        last_call = MockQMessageBox.calls[-1]
        if last_call['type'] == 'information' and last_call['title'] == "Conversion Complete":
            message = last_call['message']
            print(f"  QMessageBox Reported: {message}")
            # Dummy files will lead to 0 successful conversions and errors for each format attempted.
            if "Successfully converted to OGG: 0 file(s)" in message and \
               "Successfully converted to WebM: 0 file(s)" in message and \
               "Encountered errors with 1 file(s)" in message and \
               "File test_video1.mp4: Failed to convert test_video1.mp4 to OGG" in message and \
               "File test_video1.mp4: Failed to convert test_video1.mp4 to WebM" in message:
               reported_correctly = True
    
    print_test_result(f"{test_name} - Error Reporting for Dummy Files", reported_correctly)

def main():
    print("Initializing QApplication and VideoConverterApp...")
    # QApplication.instance() might return None if no app was ever created.
    # We must ensure one QApplication exists for widget creation within VideoConverterApp.
    # Even if not shown, widgets need an app context.
    qt_app = QApplication.instance() 
    if not qt_app:
        qt_app = QApplication(sys.argv)
    
    window = multiple_videos_convert.VideoConverterApp() # Use the module's VideoConverterApp
    
    try:
        setup_test_environment()
        
        test_case_1_ui_interaction_file_addition(window)
        test_case_2_format_selection_conversion(window)
        test_case_3_output_reporting(window)

    except Exception as e:
        print(f"An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_test_environment()
        print("\nTesting finished.")

if __name__ == "__main__":
    main()
