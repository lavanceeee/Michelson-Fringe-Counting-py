# Kama

<div align="left">
  <a href="./readme/chinese.md">
    <img src="https://img.shields.io/badge/language-中文-blue.svg" alt="Switch to Chinese">
  </a>
  <a href="https://kama.2jone.top/" target="_blank">
    <img src="https://img.shields.io/badge/Official_Website-kama.2jone.top-green.svg" alt="Official Website">
  </a>
</div>

## Overview

Kama is an cross-platform desktop fostwear designed for <u>Michelson fringe counting</u>. 

It enables **real-time capture**, **processing** and **data analyse**.

<table>
  <tr>
    <td width="50%">
      <img src="./readme/pictures/main_page.png" alt="main_page" width="100%">
    </td>
    <td width="50%">
      <img src="./readme/pictures/center_mark.png" alt="center_mark" width="100%">
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="./readme/pictures/counting.png" alt="counting" width="100%">
    </td>
    <td width="50%">
      <img src="./readme/pictures/data_processing.png" alt="data_processing" width="100%">
    </td>
  </tr>
</table>

## Highlights

- **High Degree of Project Engineering**

  The code structure is clear and strictly follows the programming practices of high cohesion and low coupling.

- **Stable and Efficient Software**

  With the support of native Qt, Qthread multi-threading, etc., the software has excellent support for data processing and real-time analysis.

- **Innovation Based on Basic Principles**

  This project is based on basic libraries such as OpenCV. I have made innovations and improvements to the algorithms after a detailed understanding of OpenCV's algorithm encapsulation, which has taught me a lot!

## Features

- **Ring Center Detection**: Detects interference ring centers using traditional algorithms based on <u>OpenCV</u>

- **Real-time Image Acquisition**: Captures live images from the [IP camera](https://en.wikipedia.org/wiki/IP_camera) for real-time observation.

- **Brightness Analysis for Counting**: The counting method based on brightness analysis provides stable and highly accurate results.

- **Data Visualization**: Counting results displayed based on [pyqtgraph](https://www.pyqtgraph.org/).

- **Interactive Interface**: GUI are poewred by [Qt](https://doc.qt.io/qtforpython-6/), a High performance GUI framework.

## Stack

- **Programming Language**: Python
- **Image Processing**: OpenCV
- **GUI Framework**: PyQt
- **Algorithm Supporting**: Numpy Scipy

## Others

[Official website](https://kama.2jone.top) of Kama, where you can get detailed information about this software, including the detailed technology stack and help documents. :)

[Center Finder algorithm](https://github.com/lavanceeee/interference-ring-iden) of Kama, to learn how I implemented the center-finding algorithm and to see the source code.