#include <Arduino.h>

int counter = 0;

void setup()
{
  Serial.begin(9600);
}

void loop(){
  counter++;
  if (counter % 3 == 0)
  {
    if (counter % 5 ==0)
    {
      Serial.println("FIZZ BUZZ");
      /* code */
    }
    else
    {
      Serial.println("BUZZ");
    }
    
    /* code */
  }
  else 
  {
    if (counter % 5 ==0)
    {
      Serial.println("Buzz");
      /* code */
    }
    else{
      Serial.println(counter);
    }
  }

  
  
  


  delay(500);
}