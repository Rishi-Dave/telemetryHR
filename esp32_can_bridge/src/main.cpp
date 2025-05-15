#include <Arduino.h>
#include "driver/twai.h"

// --- Pin Definitions ---
// TWAI (CAN bus) pins
#define TWAI_TX_PIN GPIO_NUM_4
#define TWAI_RX_PIN GPIO_NUM_5

// UART pins for communication with Jetson Nano (using Serial2)
// IMPORTANT: Change these to the actual GPIOs you connect to the Jetson Nano!
#define ESP_UART_TX_PIN GPIO_NUM_17 // Example: Connect to Jetson's UART RX (Pin 10 on 40-pin header)
#define ESP_UART_RX_PIN GPIO_NUM_18 // Example: Connect to Jetson's UART TX (Pin 8 on 40-pin header)

// --- Configuration ---
#define UART_BAUD_RATE 115200 // Baud rate for ESP32-Jetson UART link
// CAN bus speed is set in twai_timing_config_t

// Define which hardware serial port to use for Jetson communication
HardwareSerial& JetsonSerial = Serial2;

void setup() {
  // Start USB Serial for debugging
  Serial.begin(115200);
  while (!Serial) {
    delay(10); // wait for serial port to connect.
  }
  Serial.println("ESP32 CAN-to-UART Bridge Starting...");

  // Start UART for Jetson Nano
  JetsonSerial.begin(UART_BAUD_RATE, SERIAL_8N1, ESP_UART_RX_PIN, ESP_UART_TX_PIN);
  Serial.println("UART for Jetson Nano initialized.");
  JetsonSerial.println("ESP32 Connected to Jetson via UART");

  // Initialize TWAI driver
  twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TWAI_TX_PIN, TWAI_RX_PIN, TWAI_MODE_NORMAL);
  twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS(); // 500kbps
  twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

  Serial.println("Initializing TWAI driver...");
  if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
    Serial.println("TWAI Driver installed.");
  } else {
    Serial.println("Failed to install TWAI driver.");
    return;
  }

  Serial.println("Starting TWAI driver...");
  if (twai_start() == ESP_OK) {
    Serial.println("TWAI Driver started.");
  } else {
    Serial.println("Failed to start TWAI driver.");
  }
}

void loop() {
  twai_message_t message;
  esp_err_t result = twai_receive(&message, pdMS_TO_TICKS(1000)); // Timeout after 1 second

  if (result == ESP_OK) {
    Serial.print("CAN Message received: ID=0x");
    Serial.print(message.identifier, HEX);
    Serial.print(", DLC=");
    Serial.print(message.data_length_code);
    Serial.print(", Data=");
    for (int i = 0; i < message.data_length_code; i++) {
      Serial.print(message.data[i], HEX);
      Serial.print(" ");
    }
    Serial.println();

    // Prepare data for UART transmission
    // 16 bits for CAN ID, 16 bits for raw data from CAN payload
    uint16_t can_id = (uint16_t)message.identifier;
    uint16_t raw_can_data = 0;

    if (message.data_length_code >= 2) {
      // Assuming the first two bytes of CAN data are the 16-bit raw value
      raw_can_data = (uint16_t)(message.data[0] << 8) | message.data[1];
    } else if (message.data_length_code == 1) {
      // If only one byte, use it as low byte, high byte is 0
      raw_can_data = (uint16_t)message.data[0];
    } 
    // If DLC is 0, raw_can_data remains 0
    
    // Debug print the values to be sent
    Serial.print("Sending to Jetson: CAN ID=0x");
    Serial.print(can_id, HEX);
    Serial.print(", Raw Data=0x");
    Serial.println(raw_can_data, HEX);

    uint8_t uart_packet[4];
    uart_packet[0] = (can_id >> 8) & 0xFF;      // CAN ID MSB
    uart_packet[1] = can_id & 0xFF;             // CAN ID LSB
    uart_packet[2] = (raw_can_data >> 8) & 0xFF; // Raw Data MSB
    uart_packet[3] = raw_can_data & 0xFF;        // Raw Data LSB

    JetsonSerial.write(uart_packet, 4);

  } else if (result == ESP_ERR_TIMEOUT) {
    // No message received within timeout
    // Serial.println("CAN Receive Timeout"); // Optional: can be chatty
  } else {
    Serial.print("Failed to receive CAN message, error: ");
    Serial.println(esp_err_to_name(result));
  }
  delay(10); // Small delay
}
