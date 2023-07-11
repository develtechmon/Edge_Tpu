#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(4, 5); // CE, CSN 

//const byte address[6] = "00001";
const uint64_t address = 0xE8E8F0F0E1LL;

char receivedData[32] = "";
int xAxis, yAxis, Zaxis;

int guided_flag = 0;
int land_flag = 0;
int takeoff_flag = 0;
int guided_onetime = 0;
int land_onetime = 0;

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
  //Serial.println("Receive the data");
  if(radio.available()> 0)
  {
    byte Array[6];
    radio.read(&Array, sizeof(Array));
    
    Serial.println(Array[3]);

    //for (int i = 0; i < 6; i++)
    {
    // Serial.println(Array[i]);


    if (Array[1] == 1 && land_flag==0){
      Serial.println('l');
      guided_flag = 1;
      // guided_onetime = 0;
    }

     if (Array[0] == 1 && guided_flag==1)
    {
          Serial.println('g');
          takeoff_flag = 1;

          if (takeoff_flag == 1){
          Serial.println(Array[3]);
          // land_flag = 0;
        }
    }

    } 
    //radio.read(&received_data, sizeof(Received_data));
    last_Time = millis();
  }
}


void loop() {
  receive_the_data();
  //ch1_value = received_data.ch1;

  //Serial.println(ch1_value);

 }
