/*********** COMMON ***********/

// Hardware Serial2 pins
#define RXD2 16
#define TXD2 17

// Hardware LED
#define LED_BUILTIN 2

// for BT: power up press nothing
// for BLE: 0.5s after power up, press and hold BOOT BTN for 1s
// Input Pin 0 (BTN BOOT): 1:BT (not pressed) 0:BLE (pressed)
#define PIN_BLE 0

/*********** BLUETOOTH CLASSIC ***********/

// This example code is in the Public Domain (or CC0 licensed, at your option.)
// By Evandro Copercini - 2018
//
// This example creates a bridge between Serial and Classical Bluetooth (SPP)
// and also demonstrate that SerialBT have the same functionalities of a normal Serial
// Note: Pairing is authenticated automatically by this device

#include "BluetoothSerial.h"

#define BT_NAME "SynScan_BT"

/*********** BLUETOOTH LOW ENERGY ***********/

#define BLE_NAME "SynScan_BLE"
#define BLE_NAME_SHORT "SynScan"

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

BLEServer *pServer = NULL;
BLECharacteristic *pTxCharacteristic;

bool deviceConnected = false;
bool oldDeviceConnected = false;

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#if 0
// serial terminal works
#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"  // UART service UUID nordic nRF
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
#endif
#if 1
// serial terminal works
#define SERVICE_UUID             "0000ffe0-0000-1000-8000-00805f9b34fb"  // UART service UUID Telit TIO
#define CHARACTERISTIC_UUID_TXRX "0000ffe1-0000-1000-8000-00805f9b34fb"
#endif
#if 0
// serial terminal works
#define SERVICE_UUID           "49535343-FE7D-4AE5-8FA9-9FAFD205E455"  // UART service UUID microchip RN4871
#define CHARACTERISTIC_UUID_RX "49535343-8841-43F4-A8D4-ECBE34729BB3"
#define CHARACTERISTIC_UUID_TX "49535343-1E4D-4BD9-BA61-23C647249616"
#endif
#if 0
#define SERVICE_UUID           "00000001-0000-0000-0000-2b992ddfa232"  // maybe synscan
#define CHARACTERISTIC_UUID_RX "00000002-0000-0000-0000-2b992ddfa232"  // Mount->SynScan app
#define CHARACTERISTIC_UUID_TX "00000003-0000-0000-0000-2b992ddfa232"  // SynScan app->Mount
#endif
#if 0
// serial terminal doesn't work "gatt status 133"
#define SERVICE_UUID           "0000fefb-0000-1000-8000-00805f9b34fb"  // UART service UUID Telit TIO
#define CHARACTERISTIC_UUID_RX "00000002-0000-1000-8000-00805f9b34fb"
#define CHARACTERISTIC_UUID_TX "00000001-0000-1000-8000-00805f9b34fb"
#endif

// ManufacturerData makes BLE device appear
// in connect list on android synscan pro 2.5.2

// on windows synscan 2.5.2 BLE device will appear
// on the connect list regardless of ManufacturerData

// first 2 chars "h." (hex 0x68 0x2e) encode manufacturer id 0x2e68
// ghydra found it:
// void FUN_140137c80(longlong *param_1)
// this = (QByteArray *)QBluetoothDeviceInfo::manufacturerData(pQVar7,local_90,0x2e68);
// pcStack_50 = QByteArrayView::castHelper("54806524");
#define ManufacturerData "h.54806524"

// see https://esp32.com/viewtopic.php?t=16492
BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();

// *********** COMMON CODE **************
void (*loop_selected)(void); // pointer to loop function BT or BLE

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
    Serial.println("\nwrite");
    String rxValue = pCharacteristic->getValue();
    #if 0
    if (rxValue.length() > 0)
    {
      digitalWrite(LED_BUILTIN, LOW);  // turn the LED off
      for (int i = 0; i < rxValue.length(); i2b992ddfa232++)
      {
        Serial2.write(rxValue[i]);
        Serial.write(rxValue[i]);
        delay(1);
      }
    }
    #else
    if (rxValue.length() > 0)
    {
      digitalWrite(LED_BUILTIN, LOW);  // turn the LED off
      Serial2.write(rxValue.c_str(), rxValue.length());
      Serial.write(rxValue.c_str(), rxValue.length());
    }
    #endif
  }
};

void setup_ble()
{
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  // Create the BLE Device
  BLEDevice::init(BLE_NAME);

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  #ifdef CHARACTERISTIC_UUID_TXRX
  // one characteristic for both RX and TX
  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_TXRX,
    BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE);
  pTxCharacteristic->addDescriptor(new BLE2902());
  pTxCharacteristic->setCallbacks(new MyCallbacks());

  /*
  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_TXRX,
    BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE);
  */
  #else
  // separate characteristics for RX and TX
  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);
  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE);
  pRxCharacteristic->setCallbacks(new MyCallbacks());
  #endif

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  oAdvertisementData.setShortName(BLE_NAME_SHORT);
  oAdvertisementData.setManufacturerData(ManufacturerData);
  pAdvertising->setAdvertisementData(oAdvertisementData);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMinPreferred(0x12);

  // Start the service
  pService->start();

  // control the LED
  pinMode(LED_BUILTIN, OUTPUT);

  // setup detailed advertising response

  // Start advertising
  pAdvertising->start();
  Serial.write("Bluetooth Low Energy Serial: ");
  Serial.println(BLE_NAME);
}

#if 0
void setup_ble_old()
{
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  // Create the BLE Device
  BLEDevice::init(BLE_NAME);

  // Create the BLE Server
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);
  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE);
  pRxCharacteristic->setCallbacks(new MyCallbacks());

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();

  // Start the service
  pService->start();

  // control the LED
  pinMode(LED_BUILTIN, OUTPUT);

  // setup detailed advertising response

  // Start advertising
  pServer->getAdvertising()->start();
  Serial.write("Bluetooth Low Energy Serial: ");
  Serial.println(BLE_NAME);
}
#endif

void loop_ble()
{
  uint8_t txValue;

  if (deviceConnected)
  {
    if(Serial2.available())
    {
      Serial.println("\nread");
      digitalWrite(LED_BUILTIN, LOW);  // turn the LED on
      txValue = Serial2.read();
      pTxCharacteristic->setValue(&txValue, 1);
      pTxCharacteristic->notify();
      Serial.write(txValue);
    }
    //delay(10);  // bluetooth stack will go into congestion, if too many packets are sent
  }

  // disconnecting
  if (!deviceConnected && oldDeviceConnected)
  {
    delay(500);                   // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising();  // restart advertising
    Serial.println("Disconnected");
    oldDeviceConnected = deviceConnected;
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected)
  {
    // do stuff here on connecting
    oldDeviceConnected = deviceConnected;
    Serial.println("Connected");
  }
  digitalWrite(LED_BUILTIN, deviceConnected);
}


// This example code is in the Public Domain (or CC0 licensed, at your option.)
// By Evandro Copercini - 2018
//
// This example creates a bridge between Serial and Classical Bluetooth (SPP)
// and also demonstrate that SerialBT have the same functionalities of a normal Serial
// Note: Pairing is authenticated automatically by this device

// Check if Bluetooth is available
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

// Check Serial Port Profile
#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Port Profile for Bluetooth is not available or not enabled. It is only available for the ESP32 chip.
#endif

BluetoothSerial SerialBT;

void setup_bt() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  SerialBT.begin(BT_NAME);  //Bluetooth device name
  //SerialBT.deleteAllBondedDevices(); // Uncomment this to delete paired devices; Must be called after begin
  Serial.print("Bluetooth Classic Serial: ");
  Serial.println(BT_NAME);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop_bt() {
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

/************ COMMON ***********/
void setup()
{
  pinMode(PIN_BLE, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  printf("Hold BOOT while BLUE LED ON for BLE mode\n");
  delay(1500);
  digitalWrite(LED_BUILTIN, LOW);
  if(digitalRead(PIN_BLE) != 0)
  {
    setup_ble();
    loop_selected = loop_ble;
  }
  else
  {
    setup_bt();
    loop_selected = loop_bt;
  }
}

void loop()
{
  (*loop_selected)();
}
