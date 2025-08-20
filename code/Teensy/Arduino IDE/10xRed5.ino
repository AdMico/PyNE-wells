//
// Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM
//
// @developers: Adam Micolich
//
// Very basic algorithm that lights every second LED one by one then turns them off again.
// Relies on 10xLED chip with LEDs connected to Teensy4.1 pins 14-18, each with 220 ohm resistors in series to ground.
// Has no interaction with other PyNE-wells code, it's purely for hardware test.
//

int led1Pin = 18;
int led2Pin = 17;
int led3Pin = 16;
int led4Pin = 15;
int led5Pin = 14;
int counter = 0;

// The setup() method runs once, when the sketch starts

void setup()   {                
  // initialize the digitals pin as an outputs
  pinMode(led1Pin, OUTPUT);
  pinMode(led2Pin, OUTPUT);
  pinMode(led3Pin, OUTPUT);
  pinMode(led4Pin, OUTPUT);
  pinMode(led5Pin, OUTPUT);
}

// the loop() method runs over and over again,

void loop()                     
{
  if (counter >= 3){
    return;
  }
  digitalWrite(led1Pin, HIGH);
  delay(500);
  digitalWrite(led2Pin, HIGH);
  delay(500);
  digitalWrite(led3Pin, HIGH);
  delay(500);
  digitalWrite(led4Pin, HIGH);
  delay(500);
  digitalWrite(led5Pin, HIGH);
  delay(500);
  digitalWrite(led1Pin, LOW);
  delay(500);
  digitalWrite(led2Pin, LOW);
  delay(500);
  digitalWrite(led3Pin, LOW);
  delay(500);
  digitalWrite(led4Pin, LOW);
  delay(500);
  digitalWrite(led5Pin, LOW);
  delay(500);
  counter++;
}