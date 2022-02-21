#include <Arduino.h>

void setup() 
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (!Serial);

}

void loop()
{
  if (Serial.available())
  {
    int state = Serial.parseInt();
    if (state == 1)
    {
     digitalWrite(LED_BUILTIN, HIGH); 
     Serial.println("LED is now ON");
    }
    if (state == 2)
    {
     digitalWrite(LED_BUILTIN, LOW);
     Serial.println("LED is now OFF");
    }  
  }
}
