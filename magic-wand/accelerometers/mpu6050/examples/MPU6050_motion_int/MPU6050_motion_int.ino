#include <avr/sleep.h>

#include <Wire.h>
 //Analog port 4 (A4) = SDA (serial data)
//Analog port 5 (A5) = SCL (serial clock)
#define SIGNAL_PATH_RESET 0x68
#define I2C_SLV0_ADDR 0x37
#define ACCEL_CONFIG 0x1C
#define MOT_THR 0x1F // Motion detection threshold bits [7:0]
#define MOT_DUR 0x20 // Duration counter threshold for motion interrupt generation, 1 kHz rate, LSB = 1 ms
#define MOT_DETECT_CTRL 0x69
#define INT_ENABLE 0x38
#define WHO_AM_I_MPU6050 0x75 // Should return 0x68
#define INT_STATUS 0x3A
//when nothing connected to AD0 than address is 0x68
#define ADO 0
#if ADO
#define MPU6050_ADDRESS 0x69 // Device address when ADO = 1
#else
#define MPU6050_ADDRESS 0x68 // Device address when ADO = 0
#endif

int wakePin = 2; // pin used for waking up  
int led = 13;
int flag = 0;

void wakeUpNow() { // THE PROGRAM CONTINUES FROM HERE AFTER WAKING UP    (i.e. after getting interrupt)
  // execute code here after wake-up before returning to the loop() function  
  // timers and code using timers (serial.print and more...) will not work here.  
  // we don't really need to execute any special functions here, since we  
  // just want the thing to wake up 

  delay(500);
  Serial.println("WOKEN UP !!!!!!!!!!");
  delay(500);
  int count = 10;
  while (count != 0) {
    delay(1000);
    count--;
    Serial.println(count);
    delay(1000);
  }
  // precautionary while we do other stuff
  detachInterrupt(0);

}

/*    Example for using write byte
      Configure the accelerometer for self-test
      writeByte(MPU6050_ADDRESS, ACCEL_CONFIG, 0xF0); // Enable self test on all three axes and set accelerometer range to +/- 8 g */
void writeByte(uint8_t address, uint8_t subAddress, uint8_t data) {
  Wire.begin();
  Wire.beginTransmission(address); // Initialize the Tx buffer
  Wire.write(subAddress); // Put slave register address in Tx buffer
  Wire.write(data); // Put data in Tx buffer
  Wire.endTransmission(); // Send the Tx buffer
  //  Serial.println("mnnj");

}

//example showing using readbytev   ----    readByte(MPU6050_ADDRESS, GYRO_CONFIG);
uint8_t readByte(uint8_t address, uint8_t subAddress) {
  uint8_t data; // `data` will store the register data   
  Wire.beginTransmission(address); // Initialize the Tx buffer
  Wire.write(subAddress); // Put slave register address in Tx buffer
  Wire.endTransmission(false); // Send the Tx buffer, but send a restart to keep connection alive
  Wire.requestFrom(address, (uint8_t) 1); // Read one byte from slave register address 
  data = Wire.read(); // Fill Rx buffer with result
  return data; // Return data read from slave register
}

void setup() {

  /*
   * #define SIGNAL_PATH_RESET  0x68
     #define I2C_SLV0_ADDR      0x37
     #define ACCEL_CONFIG       0x1C 
     #define MOT_THR            0x1F  // Motion detection threshold bits [7:0]
     #define MOT_DUR            0x20  // Duration counter threshold for motion interrupt generation, 1 kHz rate, LSB = 1 ms
     #define MOT_DETECT_CTRL    0x69
     #define INT_ENABLE         0x38
     #define WHO_AM_I_MPU6050 0x75 // Should return 0x68
     #define INT_STATUS 0x3A*/
  Serial.begin(9600);
  writeByte(MPU6050_ADDRESS, 0x6B, 0x00);
  writeByte(MPU6050_ADDRESS, SIGNAL_PATH_RESET, 0x07); //Reset all internal signal paths in the MPU-6050 by writing 0x07 to register 0x68;
  writeByte(MPU6050_ADDRESS, I2C_SLV0_ADDR, 0x20); //write register 0x37 to select how to use the interrupt pin. For an active high, push-pull signal that stays until register (decimal) 58 is read, write 0x20.
  writeByte(MPU6050_ADDRESS, ACCEL_CONFIG, 0x01); //Write register 28 (==0x1C) to set the Digital High Pass Filter, bits 3:0. For example set it to 0x01 for 5Hz. (These 3 bits are grey in the data sheet, but they are used! Leaving them 0 means the filter always outputs 0.)
  writeByte(MPU6050_ADDRESS, MOT_THR, 10); //Write the desired Motion threshold to register 0x1F (For example, write decimal 20).  
  writeByte(MPU6050_ADDRESS, MOT_DUR, 40); //Set motion detect duration to 1  ms; LSB is 1 ms @ 1 kHz rate  
  writeByte(MPU6050_ADDRESS, MOT_DETECT_CTRL, 0x15); //to register 0x69, write the motion detection decrement and a few other settings (for example write 0x15 to set both free-fall and motion decrements to 1 and accelerometer start-up delay to 5ms total by adding 1ms. )   
  writeByte(MPU6050_ADDRESS, INT_ENABLE, 0x40); //write register 0x38, bit 6 (0x40), to enable motion detection interrupt.     
  writeByte(MPU6050_ADDRESS, 0x37, 160); // now INT pin is active low

  pinMode(2, INPUT); // sets the digital pin 7 as input

  pinMode(wakePin, INPUT_PULLUP); // wakePin is pin no. 2
  pinMode(led, OUTPUT); //   led is pin no. 13
  // attachInterrupt(0, wakeUpNow, LOW); // use interrupt 0 (pin 2) and run function wakeUpNow when pin 2 gets LOW

}

void sleepNow() {
  set_sleep_mode(SLEEP_MODE_PWR_DOWN); // sleep mode is set here  
  sleep_enable(); // enables the sleep bit in the mcucr register  
  delay(500);
  Serial.println("About to sleep");
  delay(500);
  attachInterrupt(0, wakeUpNow, LOW); // use interrupt 0 (pin 2) and run function  
  delay(500);
  Serial.println("Interupt attached");
  delay(500);
  sleep_mode(); // here the device is actually put to sleep...!!

  // THE PROGRAM CONTINUES FROM HERE AFTER INTERRUPT IS CLOSED
  delay(500);
  Serial.println("Continuing main program after interupt");
  delay(500);

  sleep_disable(); // first thing after waking from sleep: disable sl¯eep...  
  delay(500);
  Serial.println("Sleep disabled");
  delay(500);
}
uint16_t readdata;
void loop() {
  if (digitalRead(2) == 0) {
    {

      digitalWrite(13, 1);
      delay(100);
      digitalWrite(13, 0);
      delay(100);
    }
  }
  sleepNow(); // sleep function called here
  readdata = readByte(MPU6050_ADDRESS, 0x3A);
  Serial.print(readdata);
  Serial.print(",");
  readdata = readByte(MPU6050_ADDRESS, 0x37);
  Serial.println(readdata);

}
