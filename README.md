# ISO_CANTP
CAN TP Simulator

# CAN Transport Protocol (CAN TP) Project

This project implements a CAN Transport Protocol (CAN TP) communication system using the Python-can library. It is designed to work with the ValueCan hardware and adheres to the AUTOSAR and ISO 15765-2 standards for CAN communication. The project includes message fragmentation and reassembly as per ISO 15765-2, along with flow control and error handling.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Introduction
The CAN Transport Protocol (ISO 15765-2) is a protocol used for transmitting messages larger than the CAN frame's maximum size (8 bytes) by splitting them into smaller frames. This project simulates CAN TP communication using Python's `python-can` library and ValueCan hardware, complying with the AUTOSAR standard for automotive communication systems.

## Features
- **CAN Message Fragmentation**: Fragmentation of long messages into smaller frames for transmission.
- **Reassembly**: Reassembles the fragmented CAN frames into the original message.
- **Flow Control**: Implements ISO 15765-2 flow control, ensuring proper timing and message transmission.
- **Error Handling**: Handles errors such as timeouts and buffer overflows.
- **Virtual CAN Node Communication**: Simulates two virtual CAN nodes communicating with each other.

## Requirements
- **Hardware**:  
  - [ValueCan 4-2](https://www.intrepidcs.com/valuecan/) (or other compatible CAN hardware)
- **Software**:  
  - Python 3.9+
  - `python-can` library
  - `canmatrix` (optional, for DBC handling)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/cantp-python-project.git
   cd cantp-python-project
