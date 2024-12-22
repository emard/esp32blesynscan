// install Board -> Boards Manager -> "esp32 by espressif"
// Board: XIAO_ESP32S3
// CPU freq 80MHz (WiFi/BT) for power saving

/*********** COMMON ***********/

// Hardware Serial2 pins
#define RXD2 44
#define TXD2 43
#define BAUD 9600
// serial noise reduction 0:OFF 1:ON
#define NOISE_REDUCTION 1

// debug prints
#if 0
#define DEBUG_PRINTLN(x)  Serial.println(x)
#define DEBUG_WRITE(x)    Serial.write(x)
#define DEBUG_WRITE2(x,y) Serial.write(x,y)
#else
#define DEBUG_PRINTLN(x)
#define DEBUG_WRITE(x)
#define DEBUG_WRITE2(x,y)
#endif

// Hardware LED already defined
//#define LED_BUILTIN 2
#define LED_ON  LOW
#define LED_OFF HIGH

/*********** BLUETOOTH LOW ENERGY ***********/

// #define BLE_NAME "SynScan_b1e5" // original devices have hex from WiFi MAC to BLE name
#define BLE_NAME "SynScan_BLE"

//#define BLE_NAME_SHORT "SynScan"

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

   16-bit Attribute UUID replaces the x’s in the following:
   0000xxxx-0000-1000-8000-00805F9B34FB

   32-bit Attribute UUID replaces the x's in the following:
   xxxxxxxx-0000-1000-8000-00805F9B34FB

   https://github.com/Jakeler/ble-serial
   source ble-venv/bin/activate
   ble-scan -i hci1
   Started general BLE scan
   24:0A:C4:11:22:33 (rssi=-48): SynScan_BLE
   ble-serial -i hci1 -d 24:0A:C4:11:22:33
*/
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer *pServer = NULL;
BLECharacteristic *pTxCharacteristic;
BLECharacteristic *pRxCharacteristic;

// default is 15 normally we don't need more
#define BLE_HANDLERS 15

// direction mount->synscan
// enable one of:
// NOTIFY   faster, no required confirmation from other end
// INDICATE slower, requires confirmation from other end
// synscan works only with TX_INDICATE
#define TX_NOTIFY   0
#define TX_INDICATE 1

// TXBUF_LEN 0  to disable
// TXBUF_LEN > 0 to enable (TX_INDICATE needs it)
// recommend TXBUF_LEN 32 with TX_INDICATE 1
// [bytes] length of TX buffer
// conditions when buffer is delivered
// with optional notify/indicate signal:
// first "=" must be received then "\r" (CR)
// todo: timout, buffer full
#define TXBUF_LEN   32
// [us] timeout on serial receive, reset txbuf buffer
#define RECV_TIMEOUT_US 10000

// direction synscan->mount
// enable one or none
// if CHARACTERISTIC_UUID_TXRX is used and RX_NOTIFY is enabled
// then android serial bluetooth terminal prints repeated chars
// maybe comm is not fully correct with RX_NOTIFY with TXRX
// if notify is not enabled, synscan will keep on sending the same message
// for 1 second
// synscan works only with RX_NOTIFY
#define RX_NOTIFY   1
#define RX_INDICATE 0

bool rx_indicate = false;
bool deviceConnected = false;
bool oldDeviceConnected = false;

uint8_t txbuf[TXBUF_LEN+2]; // +2 to terminate with \n\0 for debug priting
uint32_t txbuf_index = 0;
int32_t prev_recv_us = 0, recv_us = 0;
uint8_t recv_acceptable[256];
bool expect_fw_version = false;
bool rewrite_aux_encoder = false;
bool response_detected = false;

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#if 0
// serial terminal works
#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"  // UART service UUID nordic nRF
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
#endif
#if 0
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
#if 1
// synscan works
#define SERVICE_UUID             "0000a002-0000-1000-8000-00805F9B34FB"  // SynScan has 
#define CHARACTERISTIC_UUID_RX   "0000c302-0000-1000-8000-00805F9B34FB"  // SynScan->Mount 0xc302 WRITE
#define CHARACTERISTIC_UUID_TX   "0000c306-0000-1000-8000-00805F9B34FB"  // Mount->SynScan 0xc306 INDICATE
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

// first 2 bytes "h." (hex 0x68 0x2e)
// in nRF connect appear as
// Company: Reserved ID: <0x2E68>
// following 4 bytes encode string "54806524"
// in nRF connect appear as
// 0x3534383036353234
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
    digitalWrite(LED_BUILTIN, LED_ON);  // turn the LED on
  };

  void onDisconnect(BLEServer *pServer)
  {
    deviceConnected = false;
    digitalWrite(LED_BUILTIN, LED_OFF);  // turn the LED off
  }
};

class MyCallbacks : public BLECharacteristicCallbacks
{
  void onWrite(BLECharacteristic *pCharacteristic)
  {
    //Serial.println("\nwrite");
    String rxValue = pCharacteristic->getValue();
    #if 0
    if (rxValue.length() > 0)
    {
      digitalWrite(LED_BUILTIN, LED_OFF);  // turn the LED off
      for (int i = 0; i < rxValue.length(); i++)
      {
        Serial2.write(rxValue[i]);
        DEBUG_WRITE(rxValue[i]);
        delay(1);
      }
    }
    #else
    if (rxValue.length() > 0)
    {
      digitalWrite(LED_BUILTIN, LED_OFF);  // turn the LED off
      expect_fw_version = rxValue == ":e1\r";
      if(rxValue == "AT+CWMODE_CUR?\r\n") // this is problematic command
      {
        Serial2.write(":e1\r"); // rewritten as non-problematic command :e1
        DEBUG_WRITE2(rxValue.c_str(), rxValue.length());
      }
      // fix for virtuoso heritage 90 with firmware v2.16.A1
      // problem: mount turns non stop if auxiliary encoders are not used
      // this rewrites :W2050000\r -> :W2040000\r
      // now it is not neccessary to enable auxiliary encoders
      else if(rewrite_aux_encoder && rxValue == ":W2050000\r") // this is problematic command
      {
        Serial2.write(":W2040000\r"); // rewritten as non problematic command
        DEBUG_WRITE2(rxValue.c_str(), rxValue.length());
      }
      else
      {
        Serial2.write(rxValue.c_str(), rxValue.length());
        DEBUG_WRITE2(rxValue.c_str(), rxValue.length());
      }
    }
    #endif
    #if RX_NOTIFY
    pCharacteristic->notify();
    #endif
    #if RX_INDICATE
    rx_indicate = true;
    #endif
    DEBUG_WRITE('\n');
  }
};

void reset_buffer()
{
  txbuf_index = 0;
  response_detected = false;
}

void init_recv_acceptable()
{
  memset(recv_acceptable    , 0, 256); // clear
  recv_acceptable['='] = 1;
  memset(recv_acceptable+'0', 1, 10); // 0-9 set as acceptable
  memset(recv_acceptable+'A', 1, 6); // A-F set as acceptable
  recv_acceptable['\r'] = 1;
}

void setup_ble()
{
  Serial.begin(115200);
  Serial2.begin(BAUD, SERIAL_8N1, RXD2, TXD2);

  // Create the BLE Device
  BLEDevice::init(BLE_NAME);

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(BLEUUID(SERVICE_UUID), BLE_HANDLERS);

  #ifdef CHARACTERISTIC_UUID_TXRX
  // one characteristic for both RX and TX
  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_TXRX,
  #if TX_NOTIFY
    BLECharacteristic::PROPERTY_NOTIFY |
  #endif
  #if TX_INDICATE
    BLECharacteristic::PROPERTY_INDICATE |
  #endif
    BLECharacteristic::PROPERTY_WRITE);
  pTxCharacteristic->addDescriptor(new BLE2902());
  pTxCharacteristic->setCallbacks(new MyCallbacks());
  #else
  // separate characteristics for RX and TX
  auto DescriptorTx2902 = new BLE2902();
  // Create a BLE Characteristic
  #if TX_NOTIFY
  pTxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);
  DescriptorTx2902->setNotifications(true);
  #else
  DescriptorTx2902->setNotifications(false);
  #endif
  #if TX_INDICATE
  pTxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_INDICATE);
  DescriptorTx2902->setIndications(true);
  #else
  DescriptorTx2902->setIndications(false);
  #endif
  // in nRF connect BLE2902 appears under
  // TX Characteristic
  // Descriptors:
  // Client Characteristic Configuration
  // UUID: 0x2902
  pTxCharacteristic->addDescriptor(DescriptorTx2902);

  BLEDescriptor *DescriptorRx2901 = new BLEDescriptor("2901");
  #if RX_NOTIFY
  //DescriptorRx2901->setNotifications(true);
  #else
  //DescriptorRx2901->setNotifications(false);
  #endif
  #if RX_INDICATE
  //DescriptorRx2901->setIndications(true);
  #else
  //DescriptorRx2901->setIndications(false);
  #endif
  pRxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE);
  // in nRF connect BLE2902 appears under
  // RX Characteristic
  // Descriptors:
  // Client Characteristic Configuration
  // UUID: 0x2902
  //pRxCharacteristic->addDescriptor(DescriptorRx2902);
  // Characteristic User Description
  // UUID: 0x2901
  pRxCharacteristic->addDescriptor(DescriptorRx2901);
  pRxCharacteristic->setCallbacks(new MyCallbacks());
  #endif

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  #ifdef BLE_NAME_SHORT
  oAdvertisementData.setShortName(BLE_NAME_SHORT);
  #endif
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
  DEBUG_WRITE("Bluetooth Low Energy Serial: ");
  DEBUG_PRINTLN(BLE_NAME);
  init_recv_acceptable();
}

void loop_ble()
{
  uint8_t txValue;
  static int32_t recv_us;

  if (deviceConnected)
  {
    if(Serial2.available())
    {
      //Serial.println("\nread");
      digitalWrite(LED_BUILTIN, LED_OFF);  // turn the LED on
      txValue = Serial2.read();
      recv_us = micros();
      #if 1
      // ECHO CANCELLATION, SEND ONLY RESPONSE PART
      if(txValue == '=' || txValue == '!')
      {
        response_detected = true;
        txbuf_index = 0;
      }
      #endif
      txbuf[txbuf_index++] = txValue;
      if(response_detected)
        DEBUG_WRITE(txValue);
      if(txbuf_index >= TXBUF_LEN
      || (response_detected && txValue == '\r') )
      {
        // deliver data now
        pTxCharacteristic->setValue(txbuf, txbuf_index); // txbuf_index is the length
        if(expect_fw_version)
          rewrite_aux_encoder = memcmp(txbuf,"=0210A1\r",txbuf_index) == 0;
        // reset after delivery, prepare for next data
        reset_buffer();
        Serial.write(txbuf, txbuf_index); // usb-serial
        DEBUG_WRITE('\n');
        //txbuf[txbuf_index] = '\n';
        //txbuf[txbuf_index+1] = '\0';
        //Serial.write(txbuf, txbuf_index+2); // debug print on USB serial
        #if TX_NOTIFY
        pTxCharacteristic->notify();
        #endif
        #if TX_INDICATE
        pTxCharacteristic->indicate();
        #endif
        delay(1);  // bluetooth stack will go into congestion, if too many packets are sent
     }
     else // we are still inserial available, check timeout
     {
       #if NOISE_REDUCTION
       if(recv_us-prev_recv_us > RECV_TIMEOUT_US || recv_acceptable[txValue] == 0)
       {
         // discard buffer on timeout
         // rx_indicate = false; // trying to increase chance of BLE retry
         reset_buffer();
       }
       #endif
     }
     prev_recv_us = recv_us;
    }
    #if RX_INDICATE
    if(rx_indicate)
    {
      pRxCharacteristic->indicate();
      rx_indicate = false;
    }
    #endif
    if(Serial.available()) // usb-serial
      Serial2.write(Serial.read());
  }
  else // usb-serial mode when BLE is not connected
  {
    if(Serial2.available())
      Serial.write(Serial2.read());
    if(Serial.available())
      Serial2.write(Serial.read());
    delay(1);
  }

  // disconnecting
  if (!deviceConnected && oldDeviceConnected)
  {
    delay(500);                   // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising();  // restart advertising
    DEBUG_PRINTLN("Disconnected");
    oldDeviceConnected = deviceConnected;
    // reset connection tracking states
    rx_indicate = false;
    reset_buffer();
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected)
  {
    // do stuff here on connecting
    oldDeviceConnected = deviceConnected;
    DEBUG_PRINTLN("Connected");
    // reset connection tracking states
    rx_indicate = false;
    reset_buffer();
  }
  digitalWrite(LED_BUILTIN, deviceConnected ^ LED_OFF);
}


// This example code is in the Public Domain (or CC0 licensed, at your option.)
// By Evandro Copercini - 2018
//
// This example creates a bridge between Serial and Classical Bluetooth (SPP)
// and also demonstrate that SerialBT have the same functionalities of a normal Serial
// Note: Pairing is authenticated automatically by this device

// Check if Bluetooth is available
#if 0
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif
#endif

// Check Serial Port Profile
#if 0
#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Port Profile for Bluetooth is not available or not enabled. It is only available for the ESP32 chip.
#endif
#endif


/************ COMMON ***********/
void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LED_OFF);
  setup_ble();
  loop_selected = loop_ble;
}

void loop()
{
  (*loop_selected)();
}
