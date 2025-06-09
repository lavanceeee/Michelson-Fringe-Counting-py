# Kama

## Project Overview

**Kama** is an image analysis system designed for physics experiments. It enables real-time capture, processing, and analysis of camera images, supporting functionalities such as ring detection and brightness variation measurement. The system is particularly suitable for Michelson interference fringe detection.

## Features

- **Real-time Image Acquisition**: Captures live images from the camera for experimental observation.
- **Ring Center Detection**: Detects interference ring centers using a CNN-based model *(in progress; potential transition to polar coordinate and intensity centroiding under evaluation)*.
- **Brightness Analysis**: Measures and records brightness changes at specific regions in real time.
- **Data Visualization**: Displays brightness trends through intuitive graphical charts.
- **Interactive Interface**: Provides a basic GUI for user interaction.

## Tech Stack

- **Programming Language**: Python
- **Image Processing**: OpenCV
- **Deep Learning Framework**: PyTorch
- **GUI Framework**: PyQt6

---

## Status

The system is currently in early development. Some features are functional, while others (e.g., CNN-based detection) are under active development.
