/*
    Video: https://www.youtube.com/watch?v=oCMOYS71NIU
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleNotify.cpp
    Ported to Arduino ESP32 by Evandro Copercini

   Install:
   Board manager -> esp32 by espressif

   Select board:
   Board -> esp32 -> ESP32 Dev Module

   Create a BLE server that, once we receive a connection, will send periodic notifications.
   The service advertises itself as: 6E400001-B5A3-F393-E0A9-E50E24DCCA9E
   Has a characteristic of: 6E400002-B5A3-F393-E0A9-E50E24DCCA9E - used for receiving data with "WRITE"
   Has a characteristic of: 6E400003-B5A3-F393-E0A9-E50E24DCCA9E - used to send data with  "NOTIFY"

   The design of creating the BLE server is:
   1. Create a BLE Server
   2. Create a BLE Service
   3. Create a BLE Characteristic on the Service
   4. Create a BLE Descriptor on the characteristic
   5. Start the service.
   6. Start advertising.

   In this example rxValue is the data received (only accessible inside that function).
   And txValue is the data to be sent, in this example just a byte incremented every second.
*/
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// Hardware Serial2 pins
#define RXD2 16
#define TXD2 17

// Hardware LED
#define LED_BUILTIN 2

BLEServer *pServer = NULL;
BLECharacteristic *pTxCharacteristic;
bool deviceConnected = false;
bool oldDeviceConnected = false;
uint8_t txValue = 64;

int32_t t_us = micros(); // [us] microseconds for LED blinking
int32_t led_event_us = t_us; // schedule next immediately


// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#if 1
// serial terminal works
#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"  // UART service UUID nordic nRF
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
#endif
#if 0
// serial terminal works
#define SERVICE_UUID           "49535343-FE7D-4AE5-8FA9-9FAFD205E455"  // UART service UUID microchip RN4871
#define CHARACTERISTIC_UUID_RX "49535343-8841-43F4-A8D4-ECBE34729BB3"
#define CHARACTERISTIC_UUID_TX "49535343-1E4D-4BD9-BA61-23C647249616"
#endif
#if 0
// serial terminal doesn't work "gatt status 133"
#define SERVICE_UUID           "0000fefb-0000-1000-8000-00805f9b34fb"  // UART service UUID Telit TIO
#define CHARACTERISTIC_UUID_RX "00000002-0000-1000-8000-00805f9b34fb"
#define CHARACTERISTIC_UUID_TX "00000001-0000-1000-8000-00805f9b34fb"
#endif

class MyServerCallbacks : public BLEServerCallbacks
{
  void onConnect(BLEServer *pServer)
  {
    deviceConnected = true;
    digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on
  };

  void onDisconnect(BLEServer *pServer)
  {
    deviceConnected = false;
    digitalWrite(LED_BUILTIN, LOW);  // turn the LED off
  }
};

class MyCallbacks : public BLECharacteristicCallbacks
{
  void onWrite(BLECharacteristic *pCharacteristic)
  {
    String rxValue = pCharacteristic->getValue();
    #if 0
    if (rxValue.length() > 0)
    {
      digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on
      for (int i = 0; i < rxValue.length(); i++)
      {
        Serial2.write(rxValue[i]);
        Serial.write(rxValue[i]);
        delay(1);
      }
      digitalWrite(LED_BUILTIN, LOW);  // turn the LED off
    }
    #else
    if (rxValue.length() > 0)
    {
      digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on
      Serial2.write(rxValue.c_str(), rxValue.length());
      Serial.write(rxValue.c_str(), rxValue.length());
      digitalWrite(LED_BUILTIN, LOW);  // turn the LED off
    }
    #endif
  }
};

void setup()
{
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  // Create the BLE Device
  BLEDevice::init("SynScan");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);

  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE);

  pRxCharacteristic->setCallbacks(new MyCallbacks());

  // Start the service
  pService->start();

  // control the LED
  pinMode(LED_BUILTIN, OUTPUT);

  // Start advertising
  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}

void loop()
{
  if (deviceConnected)
  {
    if(Serial2.available())
    {
      txValue = Serial2.read();
      pTxCharacteristic->setValue(&txValue, 1);
      pTxCharacteristic->notify();
      Serial.write(txValue);
      digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on
    }
    //delay(10);  // bluetooth stack will go into congestion, if too many packets are sent
  }

  // disconnecting
  if (!deviceConnected && oldDeviceConnected)
  {
    delay(500);                   // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising();  // restart advertising
    Serial.println("disconnected");
    oldDeviceConnected = deviceConnected;
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected)
  {
    // do stuff here on connecting
    oldDeviceConnected = deviceConnected;
    Serial.println("connected");
  }
}
