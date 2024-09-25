# ISO_CANTP
CAN TP Simulator

# CAN Transport Protocol (CAN TP) Project

This project implements a CAN Transport Protocol (CAN TP) communication system using the Python-can library. It is designed to work with the ValueCan hardware and adheres to the AUTOSAR and ISO 15765-2 standards for CAN communication. The project includes message fragmentation and reassembly as per ISO 15765-2, along with flow control and error handling.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Documentation](#documentaion)
- [Todos](#todos)

## Introduction
The CAN Transport Protocol (ISO 15765-2) is a protocol used for transmitting messages larger than the CAN frame's maximum size (8 bytes) by splitting them into smaller frames. This project simulates CAN TP communication using Python's `python-can` library and ValueCan hardware, complying with the AUTOSAR standard for automotive communication systems.

## Features
- **Fragmentation & Reassembly**: Fragmentation of long messages into smaller frames for transmission & Reassembles the fragmented CAN frames into the original message with different payload.
![image](https://github.com/user-attachments/assets/0f8a40e2-43a5-453e-81ad-094d18f1c0b6)

- **Flow Control**: Implements ISO 15765-2 flow control, ensuring proper timing (N_Bs, N_Cr) and message transmission.
- **Error Handling**: Handles errors such as timeouts and buffer overflows.
![image](https://github.com/user-attachments/assets/eff66330-caea-478b-b911-36d0b50a9190)

- **Support Classical CAN & CAN FD**: Compatible with both Classical CAN and CAN FD (Normal addressing)

- **Virtual CAN Node Communication**: Simulates two virtual CAN nodes communicating with each other.
- **Diffirent Scenarios*: Simulate different possible scenarios

## Requirements
- **Hardware**:
  ![image](https://github.com/user-attachments/assets/a17f2019-3ef0-4f68-b14f-f83e69468644)
  - [ValueCan 4-2](https://www.intrepidcs.com/valuecan/) (or other compatible CAN hardware)
- **Software**:  
  - Python 3.9+
  - [python-can](https://python-can.readthedocs.io/en/stable/#) library

## Documentation
- [SWC_CANTP](https://www.autosar.org/fileadmin/standards/R21-11/CP/AUTOSAR_SWS_CANTransportLayer.pdf)
- ISO 15765-2

## Todos
- Add more standard timeout mechanisms (N_As, N_Ar, N_Bs, N_Br)
- Support CAN TP multiple connections
