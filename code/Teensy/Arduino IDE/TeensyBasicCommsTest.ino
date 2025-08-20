//
// Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM
//
// @developers: Adam Micolich
//
// For use with TeensyBasicCommsTest.py only.
// Code will allow you to send a string to the Teensy, which will echo the string back to you.
// End loop using 'exit'. Code is purely for serial byte traffic check.
//

void setup() {
   Serial.begin(9600); // begin transmission
}

void loop() {
  String val;
  while (Serial.available() > 0) {
    val = val + (char)Serial.read(); // read data byte by byte and store it
  }
  Serial.print(val); // send the received data back to raspberry pi
}