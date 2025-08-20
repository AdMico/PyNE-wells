//
// Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM
//
// @developers: Adam Micolich
//
// Designed for use with TeensyBasicCommsTest.py or Control - MCC_BasicFunctionChecks.py and offers full GPIO set functionality.
// For use with TeensyBasicCommsTest.py, send commands such as 14:1 or 16:0 to turn the respective LEDs on/off.
// For use with Control - MCC_BasicFunctionChecks.py, the program will automatically run a 5-iteration loop that turns a LED on,
// runs a voltage ramp on AO0 and AO1 to +2.0V and back, turns the LED off, then moves to the next LED on each subsequent iteration.
//

int Pin; //Define variable for pin number
int Set; //Define variable for output setting

void setup() {
   Serial.begin(9600); //Establish serial comms
   pinMode(14,OUTPUT);
   pinMode(15,OUTPUT);
   pinMode(16,OUTPUT);
   pinMode(17,OUTPUT);
   pinMode(18,OUTPUT);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n'); // Read until newline
    command.trim(); // Remove any leading/trailing whitespace    
    int commandIndex = command.indexOf(':'); // Find a delimiter (e.g., semicolon) to split the string
    if (commandIndex != -1) { // If a semicolon is found
      String PinStr = command.substring(0,commandIndex);
      String SetStr = command.substring(commandIndex+1,commandIndex+2);
      Pin = PinStr.toInt();
      Set = SetStr.toInt();
//      Send back one of the parts --- Hold commented for now for use with TeensyBasicCommsTest.py to enable debugging
//      Serial.println(Set);
      if ((Pin >= 14) && (Pin <=18) && ((Set == 0) || (Set == 1))){
        if (Set == 0){
          digitalWrite(Pin,LOW);
        } else {
          digitalWrite(Pin,HIGH);
        }
        Serial.println("GPIO Set OK");     
      } else {
        Serial.println("GPIO Set Fail: Outside bounds");
      }
    } else {
      Serial.println("GPIO Set Fail: No delimiter found");
    }
  }
}