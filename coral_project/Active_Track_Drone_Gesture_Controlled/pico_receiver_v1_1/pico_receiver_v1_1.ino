#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(4, 5); // CE, CSN 

const byte address[6] = "00001";
char receivedData[32] = "";
int xAxis, yAxis, Zaxis;

// struct Received_data {
//   char ch1;

// };

// Received_data received_data;

// char ch1_value;

void setup() {
  Serial.begin(57600);
  radio.begin();
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_MIN);
  radio.setDataRate(RF24_250KBPS);
  radio.openReadingPipe(0,address);
  radio.startListening();

}

unsigned long last_Time =0;

void receive_the_data()
{
  if(radio.available()> 0)
  {
    byte Array[6];
    radio.read(&Array, sizeof(Array));
    
    Serial.println(Array[0]);
    Serial.println(Array[1])
    Serial.println(Array[3]);
    
    //radio.read(&received_data, sizeof(Received_data));
    last_Time = millis();
  }
}


void loop() {
  receive_the_data();
  //ch1_value = received_data.ch1;

  //Serial.println(ch1_value);

 }
