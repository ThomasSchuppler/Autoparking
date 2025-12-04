#include <Arduino.h>
//Bounce 2 Library importieren
#include <Bounce2.h>

//Buttons an den Pins 2 und 3
//#define BTN_YLW 2
//#define BTN_BLU 3

const int BTN_YLW = 2;
const int BTN_BLU = 3;

const int LED_GRN = 8;
const int LED_PNK = 9;

Bounce2::Button btnYellow = Bounce2::Button();
Bounce2::Button btnBlue = Bounce2::Button();

int counter = 0;

void setup() {
  Serial.begin(9600);

  pinMode(LED_GRN,OUTPUT);
  pinMode(LED_PNK,OUTPUT);

  btnYellow.attach(BTN_YLW, INPUT_PULLUP); //Hier Button auf Pin 2 zuordnen
  btnYellow.setPressedState(LOW); //Button ist Active-Low
  
  btnBlue.attach(BTN_BLU, INPUT_PULLUP);
  btnBlue.setPressedState(LOW);
}

void loop() {
  btnYellow.update();
  btnBlue.update();

  if (btnYellow.pressed())
  {
    Serial.println("Yellow pressed");

    //Naiver Ansatz --> wird später verbessert (entfernt)
    
    for (int i = 0; i < 3; i++)
    {
      
      
      for ( int i = 0; i < 3; i++)
      {
        digitalWrite(LED_GRN,HIGH);
        delay(400);
        digitalWrite(LED_GRN,LOW);
        delay(400);
      }
        for (int i = 0; i < 3; i++)
        {
        digitalWrite(LED_GRN,HIGH);
        delay(1000);
        digitalWrite(LED_GRN,LOW);
        delay(1000);
        }
        
        
      }


    }
    
    
  
  
  if (btnBlue.pressed())
  {
    Serial.println("Blue pressed");
  }

}

