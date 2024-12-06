
# MP4 to OGG & WebM Video Converter

A simple **PyQt5-based GUI desktop application** that was created using [**ChatGPT 4o**](https://chat.openai.com) to convert MP4 videos to **OGG** and **WebM** formats using **FFmpeg**. The app allows users to control output quality, including video resolution, audio bitrate, and thread count.

---


## Features

- **Batch Conversion**:
  - Convert multiple `.mp4` videos simultaneously.
  - Outputs both `.ogg` (using `libtheora` and `libvorbis`) and `.webm` (using `libvpx-vp9` and `libopus`).
  
- **Customizable Output Settings**:
  - **Video Resolution**: Choose between `480p`, `720p`, `1080p`, or retain the original resolution.
  - **Audio Bitrate**: Adjust audio quality (`64k`, `128k`, `192k`) or retain the original bitrate.
  - **OGG Quality**: Control the OGG video quality using a scale from `1` (highest quality) to `10` (lowest quality).
  - **WebM CRF**: Adjust WebM quality using the CRF parameter (`0` = lossless, higher values = lower quality).
  - **Threads**: Specify the number of threads for faster FFmpeg processing.

- **Progress Bar**:
  - Provides real-time progress updates during batch conversion.

- **Parallel Processing**:
  - Converts multiple files concurrently for optimal efficiency.

---

## Installation

### Prerequisites

1. **FFmpeg**:
   Ensure `ffmpeg` is installed.
   - On macOS (via Homebrew):
     ```bash
     brew install ffmpeg
     ```
   - On Ubuntu/Debian:
     ```bash
     sudo apt install ffmpeg
     ```
   - On Windows: [Download FFmpeg](https://ffmpeg.org/download.html)

2. **Python 3.7+**:
   Download and install Python from [python.org](https://www.python.org/).

### Install Required Python Libraries

Install the dependencies using `pip`:
```bash
pip install PyQt5
```

---

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/multiformat-video-converter.git
   cd multiformat-video-converter
   ```

2. Run the application:
   ```bash
   python multiple_videos_convert.py
   ```

3. Use the GUI to:
   - **Select Input Folder**: Choose a folder containing `.mp4` videos.
   - **Adjust Settings**:
     - Video resolution: Choose desired resolution (`480p`, `720p`, `1080p`, or `Original`).
     - Audio bitrate: Set desired bitrate (`64k`, `128k`, `192k`, or `Original`).
     - OGG quality: Input a value between `1` (best quality) and `10` (lowest quality).
     - WebM CRF: Input a value between `0` (lossless) and `63` (lowest quality).
     - Threads: Specify the number of FFmpeg threads for parallel processing.
   - **Start Conversion**: Converted `.ogg` and `.webm` files will be saved in the `converted` folder inside the input folder.

---

## Screenshots

### Main Interface
![Main Interface](path/to/screenshot-main-interface.png)

### Conversion in Progress
![Conversion Progress](path/to/screenshot-progress.png)

---

## Code Overview

### Main Components

- **GUI (PyQt5)**:
  - Dropdowns for video resolution and audio bitrate.
  - Input fields for OGG quality, WebM CRF, and threading.
  - A button to select the input folder and start conversion.

- **Backend (FFmpeg)**:
  - Uses FFmpeg for video and audio conversion:
    - **OGG**: Video codec `libtheora`, audio codec `libvorbis`.
    - **WebM**: Video codec `libvpx-vp9`, audio codec `libopus`.
  - Parallel processing using Python’s `ThreadPoolExecutor`.

---

## Customization

Feel free to modify the app to suit your needs:
- Add more formats (e.g., AVI, MKV).
- Customize FFmpeg parameters to enhance performance or compatibility.
- Extend error handling for edge cases.

---

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add a new feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-branch
   ```
5. Create a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

### Acknowledgments

- [PyQt5](https://pypi.org/project/PyQt5/)
- [FFmpeg](https://ffmpeg.org/)

---

### TODO

- ✅ Add a progress bar for better visual feedback during conversion.
- ➡️ Implement drag-and-drop functionality for file selection.
- ➡️ Support additional output formats (e.g., AVI, MKV).
- ➡️ Add pause/resume functionality for conversions.
- ➡️ Display estimated time remaining for conversions.
- ➡️ Enhance performance and speed.

---
