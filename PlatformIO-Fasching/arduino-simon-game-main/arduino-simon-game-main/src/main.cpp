#include <Arduino.h>

int counter = 0;

void setup() {
  Serial.begin(9600);
}

/* Digit table for the 7-segment display */

void loop() {
  counter ++;

  if (counter % 3 == 0)
  {
    if (counter % 5 == 0)
    {
      Serial.print("Fizz Buzz");
    }
    else
    {
      Serial.print("Fizz ");
      
    }
    
    
    
  }
  else
  {
    if (counter % 5 == 0)
    {
      Serial.print(" Buzz");
      
    }
    else
    {
      Serial.println("counter");
      
    }
    
    
  }
  
  



  delay(500);
  
}
