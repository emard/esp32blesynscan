// This example code is in the Public Domain (or CC0 licensed, at your option.)
// By Evandro Copercini - 2018
//
// This example creates a bridge between Serial and Classical Bluetooth (SPP)
// and also demonstrate that SerialBT have the same functionalities of a normal Serial
// Note: Pairing is authenticated automatically by this device

#include "BluetoothSerial.h"

String device_name = "BTSynScan";

// Hardware Serial2 pins
#define RXD2 16
#define TXD2 17

// Hardware LED
#define LED_BUILTIN 2

// Check if Bluetooth is available
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

// Check Serial Port Profile
#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Port Profile for Bluetooth is not available or not enabled. It is only available for the ESP32 chip.
#endif

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  SerialBT.begin(device_name);  //Bluetooth device name
  //SerialBT.deleteAllBondedDevices(); // Uncomment this to delete paired devices; Must be called after begin
  Serial.printf("Bluetooth classic serial \"%s\"\n", device_name.c_str());
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  uint8_t a;
  if (Serial2.available()) {
    a = Serial2.read();
    SerialBT.write(a);
    Serial.write(a);
    digitalWrite(LED_BUILTIN, LOW);
  }
  if (SerialBT.available()) {
    a = SerialBT.read();
    Serial2.write(a);
    Serial.write(a);
    digitalWrite(LED_BUILTIN, LOW);
  }
  delay(1);
  digitalWrite(LED_BUILTIN, SerialBT.connected(0));
}
