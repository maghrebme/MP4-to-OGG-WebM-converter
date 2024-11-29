
# MP4 to OGG & WebM Video Converter

A simple and intuitive **PyQt5-based GUI desktop application** that was created using [**ChatGPT 4o**](https://chat.openai.com) to convert MP4 videos to **OGG** and **WebM** formats using **FFmpeg**. The app allows users to control output quality, including video resolution, audio bitrate, and thread count.

---

## Features

- **Convert MP4 to OGG and WebM:**
  - Video Codec: `libtheora` (OGG), `libvpx-vp9` (WebM)
  - Audio Codec: `libvorbis` (OGG), `libopus` (WebM)
- **Customizable Output Settings:**
  - **Video Resolution**: Choose from `480p`, `720p`, `1080p`, or retain the original resolution.
  - **Audio Bitrate**: Adjust audio quality (`64k`, `128k`, `192k`) or retain the original bitrate.
  - **Threads**: Configure the number of FFmpeg threads for faster parallel processing.
- **Parallel Conversion**: Converts multiple videos simultaneously using Python’s `concurrent.futures` for efficiency.
- **User-Friendly GUI**: Select input folder, adjust settings, and start conversion with just a few clicks.

---

## Installation

### Prerequisites

1. **FFmpeg**: Ensure `ffmpeg` is installed.
   - On macOS (via Homebrew):
     ```bash
     brew install ffmpeg
     ```
   - On Ubuntu/Debian:
     ```bash
     sudo apt install ffmpeg
     ```
   - On Windows: [Download FFmpeg](https://ffmpeg.org/download.html)

2. **Python 3.7+**: Ensure Python is installed. Download it from [python.org](https://www.python.org/).

### Install Required Python Libraries

Install the dependencies using `pip`:
```bash
pip install PyQt5
```

---

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mp4-to-ogg-webm-converter.git
   cd mp4-to-ogg-webm-converter
   ```

2. Run the application:
   ```bash
   python advanced_video_converter_gui.py
   ```

3. Use the GUI to:
   - **Select Input Folder**: Choose a folder containing `.mp4` videos.
   - **Adjust Settings**:
     - Video resolution: Select desired output resolution (`480p`, `720p`, `1080p`, or `Original`).
     - Audio bitrate: Choose bitrate (`64k`, `128k`, `192k`, or `Original`).
     - FFmpeg threads: Set the number of threads for parallel processing.
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
  - Input field for thread count.
  - Button to select the input folder and start conversion.
- **Backend (FFmpeg)**:
  - Video and audio conversion powered by FFmpeg with the following codecs:
    - Video: `libtheora` (OGG), `libvpx-vp9` (WebM)
    - Audio: `libvorbis` (OGG), `libopus` (WebM)
- **Parallel Processing**:
  - Converts multiple videos concurrently using Python's `ThreadPoolExecutor`.

### File Structure

- `advanced_video_converter_gui.py`: Main application script.
- `README.md`: Project documentation.

---

## Customization

Feel free to modify the app to suit your needs:
- **Additional Formats**: Extend the FFmpeg commands to support other video/audio formats.
- **Error Handling**: Add more robust error handling for edge cases.

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

- Add a progress bar for better visual feedback during conversion.
- Support more input/output formats.

---
