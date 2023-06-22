#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "Wire.h"       
#include "I2Cdev.h"     
#include "MPU6050.h"   

//Define variables for Gyroscope and Accelerometer data
MPU6050 mpu;
int16_t ax, ay, az;
int16_t gx, gy, gz;


// Define Joystick Pin
int xValue = 0 ;
int bValue = 0 ;

//Declare pin state
byte Array[6];
#define land 2
#define guided 3

//Declare pin state
char c;

RF24 radio(7, 8); // CE, CSN // nano

const byte address[6] = "00001";

//Create a struct that do not exceed 32 bytes
struct Data_to_be_sent {
  char ch1;
  //byte ch2;
};

Data_to_be_sent sent_data;

void setup() {
  Serial.begin(57600);

  Wire.begin();

  pinMode(land, INPUT_PULLUP);
  pinMode(guided, INPUT_PULLUP);

  pinMode(6,INPUT); 
	digitalWrite(6,HIGH);	
  
  mpu.initialize();

  radio.begin();
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_MIN);
  radio.setDataRate(RF24_250KBPS);
  radio.openWritingPipe(address);
  radio.stopListening();  

}

void loop() {

  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Read Potentiometer
  int data = analogRead(A0);
  int throttle = map(data,0,1023,2046,1050);
  
  //Joystick Parameter
  xValue = analogRead(A1);	
	bValue = digitalRead(8);	

  int x_joy_axis = map(xValue, 0, 1023, 0, 255); //Send X Joystick axis data

  //Accelerometer and Gyroscope
  int x_axis = map(ax, -17000, 17000, 0, 255);  //Send X axis data
  int y_axis = map(ay, -17000, 17000, 0, 255);  //Send Y axis data
	  
  Array[0] = digitalRead(land);
  Array[1] = digitalRead(guided);

  Serial.print("Roll R = ");
  Serial.print(x_axis);
  Serial.print("  ");

  Serial.print("Pitch P = ");
  Serial.print(y_axis);
  Serial.print("  ");

  Serial.print("Yaw Left = ");
  Serial.print(x_joy_axis);
  Serial.print("  ");

  Serial.print("Yaw Right = ");
  Serial.print(x_joy_axis);
  Serial.println("  ");

  if (x_axis < 50){
    Serial.print("Move Right");
    Serial.println("  ");
    Array[3] = 'd';
  }

  else if (x_axis > 200){
    Serial.print("Move Left");
    Serial.println("  ");
    Array[3] = 'a';
  }

  else if (y_axis < 70){
    Serial.print("Move Forward");
    Serial.println("  ");
    Array[3] = 'w';
  }

  else if (y_axis > 200){
    Serial.print("Move Backward");
    Serial.println("  ");
    Array[3] = 's';
  }

  else if (x_joy_axis < 30){
    Serial.print("Yaw Left");
    Serial.println(" ");
    Array[3] = 'yl';
  }

  else if (x_joy_axis > 230){
    Serial.print("Yaw Right");
    Serial.println(" ");
    Array[3] = 'yr';
  }


  else {
    Serial.println("Center");
    // Array[4] = 'x';
    Array[3] = 'x';
  }


  radio.write(&Array, sizeof(Array));

  delay(50);

}
