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
#define guide 3
#define yaw_switch 6

RF24 radio(7, 8); // CE, CSN // nano

//const byte address[6] = "00001";
const uint64_t address = 0xE8E8F0F0E1LL;

void setup() {
  Serial.begin(57600);

  Wire.begin();

  pinMode(land, INPUT_PULLUP);
  pinMode(guide, INPUT_PULLUP);
  pinMode(yaw_switch, INPUT_PULLUP);

  //pinMode(6,INPUT); 
	//digitalWrite(6,HIGH);	
  
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
  Array[1] = digitalRead(guide);
  Array[2] = digitalRead(yaw_switch);    
  Serial.println(x_axis);

  if (x_axis < 60 &&  Array[2] == 1){
    Serial.print("Move Right"); //move forward - w
    Serial.println("  ");
    Array[3] = 'w'; // - original d
  }

  else if (x_axis > 200 && Array[2] == 1){
    Serial.print("Move Left"); // move  backward
    Serial.println("  ");
    Array[3] = 's'; // - original a
  }

  else if (y_axis < 70 && Array[2] == 1){
    Serial.print("Move Forward"); // move left
    Serial.println("  ");
    Array[3] = 'a'; // - original w
  }

  else if (y_axis > 200 && Array[2] == 1){
    Serial.print("Move Backward"); //move right
    Serial.println("  ");
    Array[3] = 'd'; // - original s
  }

  // Using Yaw Switch
  else if (y_axis > 200 && Array[2] == 0){ //  else if (x_axis < 50 && Array[2] == 0){
    Serial.print("Yaw Switch Right"); 
    Serial.println("  ");
    Array[3] = 'yr';
  }

  else if (y_axis < 70 && Array[2] == 0){ // else if (x_axis > 200 && Array[2] == 0){
    Serial.print("Yaw Switch Left");
    Serial.println("  ");
    Array[3] = 'yl';
  }

  else if (x_axis < 60 &&  Array[2] == 0){
    Serial.print("Move Right"); //move forward - w
    Serial.println("  ");
    Array[3] = 'w'; // - original d
  }

  else if (x_axis > 200 && Array[2] == 0){
    Serial.print("Move Left"); // move  backward
    Serial.println("  ");
    Array[3] = 's'; // - original a
  }

  // Using Joystick Option
  else if (x_joy_axis < 30 && Array[2] == 1){
    Serial.print("Yaw Left");
    Serial.println(" ");
    Array[3] = 'yl';
  }

  else if (x_joy_axis > 230 && Array[2] == 1){
    Serial.print("Yaw Right");
    Serial.println(" ");
    Array[3] = 'yr';
  }

  else {
    Serial.println("Center");
    Array[3] = 'x';
  }

  Serial.print("Roll R = ");
  Serial.print(x_axis);
  Serial.print("  ");

  Serial.print("Pitch P = ");
  Serial.print(y_axis);
  Serial.print("  ");

  Serial.print("Yaw Left Joystick = ");
  Serial.print(x_joy_axis);
  Serial.print("  ");

  Serial.print("Yaw Right Joystick = ");
  Serial.print(x_joy_axis);
  Serial.print("  ");

  Serial.print("Yaw Switch = ");
  Serial.print(Array[2]);
  Serial.println("  ");

  radio.write(&Array, sizeof(Array));

  delay(50);

}
