# Kama - Physical Experiment Image Analysis System

## Project Overview

Kama is an image analysis system specifically designed for physical experiments, primarily for capturing, processing, and analyzing camera images in real-time. It supports circle detection and brightness measurement, suitable for various optical experiments and physical phenomenon observations.

## Key Features

- **Real-time Image Acquisition**: Captures real-time images of experimental phenomena through a camera
- **Image Preprocessing**: Supports grayscale conversion, size adjustment, and other preprocessing operations
- **Circle Detection**: High-precision circle detection based on CNN models
- **Brightness Analysis**: Real-time measurement and recording of brightness changes at specific positions in the image
- **Data Visualization**: Intuitive charts showing brightness trends
- **Interactive Interface**: User-friendly operation interface supporting parameter adjustment and data export

## System Architecture

- **Core Modules**: Image processing, detection algorithms, and data analysis engines
- **Utility Libraries**: Image conversion, preprocessing, and auxiliary functions
- **Graphical Interface**: Interactive user interface based on PyQt6
- **Algorithm Components**: Circle detection implementation containing CNN models

## Technology Stack

- **Programming Language**: Python
- **Image Processing**: OpenCV
- **Deep Learning**: CNN models based on PyTorch
- **GUI Framework**: PyQt6
- **Data Analysis**: NumPy

## Usage Instructions

1. Ensure the system has Python installed (Python 3.8+ recommended)
2. Install required dependencies: `pip install -r requirements.txt`
3. Run the program: Double-click `index.bat` or execute `python index.py`
4. Connect the camera and follow the interface prompts

## Development Environment

- **Operating System**: Windows 10/11
- **Python Version**: 3.11
- **Dependencies**: PyQt6, OpenCV, NumPy, PyTorch

## Project Directory Structure

```
kama/
├── core/             # Core functional modules
├── utils/            # Tools and helper functions
├── gui/              # Graphical interface components
├── algorithm/        # Detection algorithm implementation
├── models/           # Model weights and configurations
├── index.py          # Program entry point
└── index.bat         # Quick start script
```

## Notes

- Please ensure the camera device is properly connected before first run
- For optimal detection results, a camera with resolution no less than 720p is recommended
- Image analysis results are for reference only, actual precision is influenced by multiple factors

## Contact Information

For questions or suggestions, please contact the development team:
- Email: [lizhongpeng2@gmail.com](mailto:lizhongpeng2@gmail.com)
- Project Homepage: [https://github.com/Lizhongpeng2/Kama](https://github.com/Lizhongpeng2/Kama)

---

© 2025 Kama Development Team 