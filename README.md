# ESP32 CAN-to-UART Bridge

This project implements a bridge between CAN bus and UART using an ESP32 microcontroller. It receives CAN messages and forwards them to a host device (Jetson Nano) via UART.

## Hardware Requirements

- ESP32-S3 Development Board
- CAN Transceiver (e.g., TJA1050 or MCP2551)
- Host device with UART capability (e.g., Jetson Nano)
- USB cable for programming
- Power supply for ESP32 (USB or external)

## Pin Configuration

### ESP32-S3 Pins
- **UART (Serial2)**
  - TX: GPIO17
  - RX: GPIO18
- **CAN (TWAI)**
  - TX: GPIO4
  - RX: GPIO5
- **USB**
  - Used for programming and power

## Software Requirements

- PlatformIO (version 6.1.18 or later)
- Python 3.x (for host device script)
- Required Python packages (for host device):
  - pyserial
  - socket
  - threading

## Setup Instructions

1. **Install PlatformIO**
   - Install PlatformIO Core (CLI)
   - Add PlatformIO to your system PATH

2. **Build and Flash**
   ```bash
   # Navigate to project directory
   cd esp32_can_bridge
   
   # Build and upload to ESP32
   pio run --target upload
   
   # Monitor serial output
   pio device monitor
   ```

3. **Host Device Setup**
   - Connect ESP32 UART pins to host device
   - Run the UART listener script on the host device
   - Ensure correct baud rate (115200)

## Usage

1. **Power the ESP32**
   - Connect via USB or external power supply
   - Ensure proper power supply voltage (5V)

2. **Connect CAN Bus**
   - Connect CAN transceiver to ESP32 TWAI pins
   - Add 120Ω termination resistors
   - Connect to CAN bus network

3. **Connect to Host Device**
   - Connect ESP32 UART pins to host device
   - TX (GPIO17) → RX of host
   - RX (GPIO18) → TX of host
   - GND → GND

4. **Run Host Software**
   - Execute the UART listener script
   - Monitor received CAN messages

## Configuration

- **UART Settings**
  - Baud Rate: 115200
  - Data Bits: 8
  - Stop Bits: 1
  - Parity: None

- **CAN Bus Settings**
  - Speed: 500kbps
  - Mode: Normal
  - Protocol: Standard CAN 2.0

## Troubleshooting

1. **ESP32 Not Detected**
   - Check USB connection
   - Verify correct COM port
   - Ensure proper drivers installed

2. **No CAN Messages**
   - Verify CAN transceiver connections
   - Check CAN bus termination
   - Confirm CAN device is transmitting

3. **UART Communication Issues**
   - Verify baud rate matches on both devices
   - Check TX/RX connections
   - Ensure proper ground connection

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.