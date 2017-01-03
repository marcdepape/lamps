#include "SoftwareSerial.h"

String project_name = "motor_light_behaviour_v2";

SoftwareSerial ss(A2, A3); // RX + TX

// INCOMING
char in = 'z';
String msg = "";

// SERVO
#include <Adafruit_TiCoServo.h>
Adafruit_TiCoServo lampDial;  // create servo object to control a servo
int servoPin = 9;
int servoReadPin = A0;
int servoReadMin = 5000;
int servoReadMax = 0;
int servoSetMax = 180;
int servoSetMin = 0;
int pos = 0;
int timer = 10;

// NEO PIXELS
#include <FastLED.h>
#define top_pixels 16
#define bottom_pixels 24
#define top_neo_pin = 10;
#define bottom_neo_pin = 11;
CRGB top_neo_ring[top_pixels];
CRGB bottom_neo_ring[bottom_pixels];
#define UPDATES_PER_SECOND 100
int hue = 0;
int saturation = 0;
boolean pulse = true;

// MICROPHONE
int analogPin = A1;
boolean onOff = false;
int mic = 0;
int input = 0;
int data = 0;
const int sampleWindow = 50; // Sample window width in mS (50 mS = 20Hz)
unsigned int sample;

void setup() {
  Serial.begin(57600);
  ss.begin(57600);
  Serial.println(project_name);

  // SERVO--------------------------------------------
  pinMode(servoReadPin, INPUT);
  pinMode(servoPin, OUTPUT);

  // Servo Minimum
  lampDial.attach(servoPin);
  delay(100);
  setLow();
  for (int i = 0; i < 20; i++) {
    int input = analogRead(servoReadPin);
    if (input < servoReadMin) {
      servoReadMin = input;
    }
    delay(10);
  }
  delay(100);

  // Servo Max
  setHigh();
  for (int i = 0; i < 20; i++) {
    int input = analogRead(servoReadPin);
    if (input > servoReadMax) {
      servoReadMax = input;
    }
    delay(10);
  }

  delay(100);
  lampDial.write(servoSetMin);
  lampDial.detach();
  Serial.print("Max: ");
  Serial.print(servoReadMax);
  Serial.print("   Min: ");
  Serial.println(servoReadMin);

  // NEOPIXEL--------------------------------------------
  FastLED.addLeds<NEOPIXEL, 10>(top_neo_ring, top_pixels);
  FastLED.addLeds<NEOPIXEL, 11>(bottom_neo_ring, bottom_pixels);
}


// MAIN LOOP -------------------------------------------------------

void loop() {
  incomingRequests();
  if (pulse) {
    mic = pulseMic();
    setBottom(mic);
    setTop(map(readServo(), servoSetMin, servoSetMax, 0, 255));
  } else {
    setBoth(map(readServo(), servoSetMin, servoSetMax, 0, 255));
  }
  delay(1);
}

// SERIAL BEHAVIOUR -------------------------------------------------------

void incomingRequests() {
  while (ss.available() > 0) {
    in = ss.read();
    if (in == 'h' || in == 'l' || in == 'r' || in == 't') {
      msg = String(in);
    } else if (in == '0' || in == '1' || in == '2' || in == '3' || in == '4' || in == '5' || in == '6' || in == '7' || in == '8' || in == '9') {
      if (msg.startsWith("h") || msg.startsWith("l") || msg.startsWith("r") || msg.startsWith("t")) {
        msg = msg + String(in);
      } else {
        while (ss.available() > 0) {
          in = ss.read();
          in = 'z';
        }
      }
    } else if (in == '\n') {
      processCommand(msg);
      if (ss.available() > 0) {
        while (ss.available() > 0) {
          in = ss.read();
        }  
        in = 'z';      
      }
      msg = "";
    } else {
      sendReply("ERROR", msg);
      if (ss.available() > 0) {
        while (ss.available() > 0) {
          in = ss.read();
        }  
        in = 'z';      
      }
      msg = "";
    }
  }
}

void processCommand(String cmd) {
  String data = "";
  Serial.println("PROCESS COMMAND");
  if (cmd.length() > 1) {
    for (int i = 1; i < sizeof(cmd) - 1; i++) {
      data = data + cmd[i];
    }
  }
  cmd = cmd[0];

  // set lamp to high
  if (cmd == "h") {
    setHigh();
    Serial.println("HIGH / NO PULSE");

    // set lamp to low
  } else if (cmd == "l") {
    setLow();
    Serial.println("LOW / PULSE");

    // read current position
  } else if (cmd == "r") {
    sendReply("READ", String(readServo()));
  } else if (cmd == "t") {
    timer = data.toInt();
    sendReply("TIMER", data);
    Serial.print("TIMER: ");
    Serial.println(timer);

    // handle errors
  } else {
    sendReply("ERROR", cmd);
  }
}

int sendReply(String message, String reply) {
  Serial.print(message + "   ");
  Serial.println(reply);
  message = message + ":";
  ss.print(message);
  ss.println(reply);
}


// SERVO BEHAVIOUR -------------------------------------------------------

int readServo() {
  int reading = analogRead(servoReadPin);
  reading = constrain(map(reading, servoReadMin, servoReadMax, 0, 180), 0, 180);
  return reading;
}

void setHigh() {
  pulse = false;
  
  lampDial.attach(servoPin);
  int reading = analogRead(servoReadPin);
  reading = constrain(map(reading, servoReadMin, servoReadMax, 0, 180), 0, 180);
  while (reading <= servoSetMax) {
    lampDial.write(reading);
    setBoth(map(reading, servoSetMin, servoSetMax, 0, 255));
    reading++;
    delay(timer);
  }
  lampDial.detach();
  sendReply("HIGH", String(reading));
}

void setLow() {
  pulse = true;
  while(mic < 255) {
    mic++;
    setTop(mic);
    delay(5);
  }
  lampDial.attach(servoPin);
  int reading = analogRead(servoReadPin);
  reading = constrain(map(reading, servoSetMin*1.1, servoReadMax, 0, 180), 0, 180);
  while (reading >= servoSetMin) {
    lampDial.write(reading);
    setBoth(map(reading, servoSetMin*1.1, servoSetMax, 0, 255));
    reading--;
    delay(timer);
  }
  lampDial.detach();
  sendReply("LOW", String(reading));
}

// NEO PIXEL BEHAVIOUR ---------------------------------------------------------------

void setTop(int val) {
  for (int i = 0; i < top_pixels; i++) {
    top_neo_ring[i] = CHSV(hue, saturation, val);
    FastLED.show();
    //delay(1);
  }
}

void setBottom(int val) {
  for (int i = 0; i < bottom_pixels; i++) {
    bottom_neo_ring[i] = CHSV(hue, saturation, val);
    FastLED.show();
    //delay(1);
  }
}

void setBoth(int val) {
  for (int i = 0; i < top_pixels; i++) {
    top_neo_ring[i] = CHSV(hue, saturation, val);
    FastLED.show();
    //delay(1);
  }
  for (int i = 0; i < bottom_pixels; i++) {
    bottom_neo_ring[i] = CHSV(hue, saturation, 255 - val);
    FastLED.show();
    //delay(1);
  }
}

int pulseMic() {
  unsigned long startMillis = millis(); // Start of sample window
  unsigned int peakToPeak = 0;   // peak-to-peak level

  unsigned int signalMax = 0;
  unsigned int signalMin = 1024;

  // collect data for 50 mS
  while (millis() - startMillis < sampleWindow)
  {
    sample = analogRead(A1);
    if (sample < 1024)  // toss out spurious readings
    {
      if (sample > signalMax)
      {
        signalMax = sample;  // save just the max levels
      }
      else if (sample < signalMin)
      {
        signalMin = sample;  // save just the min levels
      }
    }
  }
  peakToPeak = signalMax - signalMin;  // max - min = peak-peak amplitude
  //Serial.print(peakToPeak);
  //Serial.print(" : ");
  peakToPeak = constrain(map(peakToPeak, 1, 30, 0, 255), 0, 255);
  return peakToPeak;
}

