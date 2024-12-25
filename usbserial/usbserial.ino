// install Board -> Boards Manager -> "esp32 by espressif"
// Board: XIAO_ESP32S3
// CPU freq 80MHz (WiFi/BT) for power saving

// works for linux wine synscan
// doesn't work for android synscan

/*********** COMMON ***********/

// Hardware Serial2 pins
#define RXD2 44
#define TXD2 43
#define BAUD 9600

#define USB_RX_US 1042
#define RECEIVE_US 50000

#define CANCEL_ECHO 0

// Hardware LED already defined
//#define LED_BUILTIN 2
#define LED_ON  LOW
#define LED_OFF HIGH

int32_t prev_usb_rx_us;
int32_t prev_transmit_false_us;

void setup()
{
  Serial.begin(BAUD); // on ESP32S3 this is usb-serial
  Serial2.begin(BAUD, SERIAL_8N1, RXD2, TXD2);

  // control the LED
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(LED_BUILTIN, LED_ON);

  int32_t time_us = micros();
  prev_usb_rx_us = time_us;
  prev_transmit_false_us = micros();
}

void loop()
{
  uint8_t usb_rx, rj12_rx;
  int32_t time_us;
  static bool halt = false;
  static bool transmit = true;
  static bool response = false;

  time_us = micros();
  if(Serial2.available() && transmit == false)
  {
    rj12_rx = Serial2.read();
    if(rj12_rx == '=')
    {
      response = true;
      prev_transmit_false_us = time_us;
      digitalWrite(LED_BUILTIN, LED_OFF);
    }
    #if CANCEL_ECHO
    if(response)
    #endif
      Serial.write(rj12_rx);
    if(rj12_rx == '\r' && response == true)
    {
      response = false;
      transmit = true;
      while(Serial2.available())
        Serial2.read();
      digitalWrite(LED_BUILTIN, LED_ON);
    }
  }
  time_us = micros();
  if(Serial.available() && time_us-prev_usb_rx_us > USB_RX_US && transmit == true)
  {
    usb_rx = Serial.read();
    Serial2.write(usb_rx);
    if(usb_rx == '\r')
    {
      transmit = false;
      prev_transmit_false_us = time_us;
      while(Serial.available())
        Serial.read();
    }
    prev_usb_rx_us += USB_RX_US;
    time_us = micros();
    if(prev_usb_rx_us < time_us)
      prev_usb_rx_us = time_us;
  }

  if(transmit == false)
    if(time_us-prev_transmit_false_us > RECEIVE_US)
    {
      transmit = true;
      response = false;
    }
    
}
