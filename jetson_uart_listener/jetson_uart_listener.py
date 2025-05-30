import serial
import time
import struct # For unpacking bytes
import socket

# --- Configuration ---
# UART port on Jetson Nano. /dev/ttyTHS1 is common for hardware UART on 40-pin header (TX=Pin8, RX=Pin10)
SERIAL_PORT = '/dev/ttyTHS1' 
BAUD_RATE = 115200  # Must match the ESP32's UART baud rate
READ_TIMEOUT = 1    # Seconds for serial read

# --- Configuration ---
LISTEN_IP = '0.0.0.0'  # Listen on all available interfaces (including Tailscale)
LISTEN_PORT = 12345   # Must match TARGET_PORT on the Jetson

def main():
    print(f"Attempting to connect to ESP32 on {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=READ_TIMEOUT)
        print("Connected to ESP32.")
        print("Listening for data...")
        
        # --- Setup ---
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((LISTEN_IP, LISTEN_PORT))
            print(f"Listening for UDP packets on {LISTEN_IP}:{LISTEN_PORT}")
        except socket.error as e:
            print(f"Error creating or binding socket: {e}")
            exit()
        
        while True:
            if ser.in_waiting >= 4: # Check if at least 4 bytes are available
                # Read the 4-byte packet (CAN ID MSB, CAN ID LSB, Raw Data MSB, Raw Data LSB)
                packet_bytes = ser.read(4)
                
                if len(packet_bytes) == 4:
                    # Unpack the 4 bytes into two 16-bit unsigned integers (big-endian)
                    # ">" for big-endian, "H" for unsigned short (16-bit)
                    can_id, raw_data_value = struct.unpack('>HH', packet_bytes)
                    
                    # Calculate the voltage
                    # The ESP32 sends data that is "voltage * 1000"
                    voltage = raw_data_value / 1000.0
                    
                    print(f"Received: CAN ID = 0x{can_id:04X} ({can_id}), "
                          f"Raw Data = 0x{raw_data_value:04X} ({raw_data_value}), "
                          f"Voltage = {voltage:.3f} V")

                    # Send data over Tailscale (UDP)
                    sock.sendto(packet_bytes, (LISTEN_IP, LISTEN_PORT))
                    print(f"Sent to {LISTEN_IP}:{LISTEN_PORT} via Tailscale")
                else:
                    # Should not happen if ser.in_waiting >= 4, but good for robustness
                    print(f"Incomplete packet received: {len(packet_bytes)} bytes")
                    # Consider flushing input buffer or other error handling
                    # ser.reset_input_buffer() 

            time.sleep(0.01) # Small delay to prevent high CPU usage

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Please ensure the ESP32 is connected and the SERIAL_PORT is correct.")
        print("You might need to run this script with sudo if you get a permission error.")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")
        if 'sock' in locals() and sock.is_open:
            sock.close()
            print("Socket closed.")

if __name__ == '__main__':
    main() 