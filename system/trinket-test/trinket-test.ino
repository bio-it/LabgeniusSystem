
#include <Wire.h>

#define DEBUG

#define BAUDRATE          115200
#define ADDRESS           8


byte receivedBuffer[32];

void setup() {
  // Clear buffer
  for(int i=0; i<32; ++i){
    receivedBuffer[i] = 0x00;
  }
#ifdef DEBUG
  Serial.begin(BAUDRATE);
  
  while (!Serial);
#endif
  Wire.begin(ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void loop() {
}

void requestEvent() {
  Wire.write(0x05);
  Wire.write(11);
  Wire.write(12);
  Wire.write(13);

  Serial.println("write called");
}

void receiveEvent(int len) {
  if (Wire.available() > 0) {
    Serial.print("Data received size :");
    Serial.println(len);

    Serial.print("Data received ");
    for(int i=0; i<len; ++i){
      byte data = Wire.read();

      Serial.print(data);
      Serial.print(",");
    }

    Serial.println("Data received complete");
  }
}
