#include <PowerFunctions.h>
#include <Wire.h>
#include <CircularBuffer.h>
#include <SimpleTimer.h>

/**
 *  Project: Bricks in the Air - dds.mil
 *  Title: Engine Control Unit
 *  
 *  Purpose: To expose people to common low level protocols that mimic aviation protocols, specifically 
 *  using I2C as a correlation to 1553.
 *    
 *    
 *  @author Dan Allen
 *  @version 1.1 7/1/20
 *  
 *  Contributers:
 *  Jason Phillips
 *    
 *  Credits:
 *    https://github.com/jurriaan/Arduino-PowerFunctions
 *    https://github.com/marcelloromani/Arduino-SimpleTimer
 */

/*
 * General Config Definitions
 */
#define ENGINE_I2C_ADDRESS 0x55
#define LEGO_IR_CHANNEL 0 //0=ch1 1=ch2 etc.
#define LEGO_MOTOR_OUTPUT_BLOCK 0x00 // 0x00 RED, 0x01 BLUE
#define SERIAL_BAUD 9600
#define I2C_RX_BUFFER_SIZE 100
#define I2C_TX_BUFFER_SIZE 200
#define STARTUP_LED_SPEED_MS  100


/*
 * Pin Definitions
 */
#define GREEN_LED 3
#define YELLOW_LED 5
#define RED_LED 6
#define LEGO_PF_PIN 10

/*
 * State Machine Definitions
 */
#define OFF 0x00
#define ON  0x01
#define DC  0x10

#define MOTOR_CRUISING_NORMAL 0x02
#define MOTOR_START_SPEED 0x00

#define PRI_OPERATION_MODE 0x00
#define SEC_OPERATION_MODE  0x01
#define MAINT_STATUS_NORMAL 0x00
#define MAINT_STATUS_DEBUG 0x01

#define REJECTED_COMMAND 0xDE
#define ACCEPTED_COMMAND 0x01
#define FAULT_DETECTED   0xDA


/*
 * I2C Comms Definitions
 */
//Commands
#define GET_ENGINE_SPEED      0x10
#define SET_ENGINE_SPEED      0x11
#define STOP_ENGINE           0x15    // This exists only to stop the engine when no on is playing
#define GET_MODE_OF_OPERATION 0x30
#define SET_MODE_OF_OPERATION 0x31
#define GET_MAINT_STATUS      0x40
#define SET_MAINT_STATUS      0x41
#define GET_LEGO_PF_CHANNEL   0x80
#define GET_LEGO_PF_COLOR     0x90
#define RESET                 0xFE

//Response
#define UNKNOWN_COMMAND   0x33
#define NO_DATA           0xFF

/*
 * Library Instantiations
 */
PowerFunctions pf(LEGO_PF_PIN, LEGO_IR_CHANNEL);   //Setup Lego Power functions pin


/*
 * Globals
 */
short volatile g_engine_speed = MOTOR_START_SPEED;
short volatile g_operation_mode = PRI_OPERATION_MODE;
short volatile g_main_status_mode = MAINT_STATUS_NORMAL;

// the timer object, used to uncouple the Lego pf call routine from I2C commands
SimpleTimer timer;

CircularBuffer<short,I2C_RX_BUFFER_SIZE> g_i2c_rx_buffer;
CircularBuffer<short,I2C_TX_BUFFER_SIZE> g_i2c_tx_buffer;

/*
 * Update motor speed by sending IR command
 */
 void update_ir_motor_speed(void) {
  //Handle the desired mode change
    switch(g_engine_speed){
      case 0:
        Serial.println(F("Engine off"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_BRK);
        break;
      case 1:
        Serial.println(F("Slow Speed 1"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD1);
        break;
      case 2:
        Serial.println(F("Slow Speed 2"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD2);
        break;
      case 3:
        Serial.println(F("Medium Speed 1"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD3);
        break;
      case 4:
        Serial.println(F("Medium Speed 2"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD4);
        break;
      case 5:
        Serial.println(F("Fast Speed 1"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD5);
        break;
      case 6:
        Serial.println(F("Fast Speed 2"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD6);
        break;
      case 7:
        Serial.println(F("Fast Speed 3"));
        pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD7);
        break;
      default:   
        Serial.println(F("Unknown Motor Speed"));         
        break;
    }
 }


/*
 * Setup method to handle I2C Wire setup, LED Pins and Serial output
 */
void setup() {
  int i;  
  Wire.begin(ENGINE_I2C_ADDRESS);
  Wire.onReceive(receiveEvent); // register event handler for recieve
  Wire.onRequest(requestEvent); // register event handler for request

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  
  Serial.begin(SERIAL_BAUD);    // start serial for output debugging
  Serial.println(F("Main Engine Control Unit is online, ready for tasking"));
  
  for (i=0; i<5; i++) {
    set_led(ON, OFF, OFF);
    delay(STARTUP_LED_SPEED_MS);
    set_led(OFF, ON, OFF);
    delay(STARTUP_LED_SPEED_MS);
    set_led(OFF, OFF, ON);
    delay(STARTUP_LED_SPEED_MS);
    set_led(OFF, ON, OFF);
    delay(STARTUP_LED_SPEED_MS);
  }

  set_led(ON, OFF, OFF);
  update_ir_motor_speed();
  
}

/*
 * The main loop of execution for the Engine Control Unit
 */
void loop() {
  timer.run();  
}

/*
 * I2c State machine
 * Needs to be non-blocking
 */
void process_i2c_request(void) {
  short command = 0xff;
  short payload = 0xff;
  if(g_i2c_rx_buffer.isEmpty() != true) {
    //clear any unsent responses
    g_i2c_tx_buffer.clear();
    //read command and pull it out of the buffer
    command = g_i2c_rx_buffer.shift();
    if(g_i2c_rx_buffer.isEmpty() != true) {
      payload = g_i2c_rx_buffer.shift();
    }
  }

  if(command != 0xff && payload != 0xff){
    //recieved a set request, need a payload
    switch(command){

      case STOP_ENGINE:
        if(payload == ON){
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          g_engine_speed = 0;
          timer.setTimeout(1, update_ir_motor_speed);   // need the timer delay to respond to i2c correctly
        }else{
          g_i2c_tx_buffer.push(REJECTED_COMMAND);
        }
        break;
      
      case SET_ENGINE_SPEED:
        // Need to expand logic to speicify when the enigne can be changed
        if(g_main_status_mode == MAINT_STATUS_DEBUG){
          if(payload >= 0 && payload <= 7){
            g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
            g_engine_speed = payload;            
            timer.setTimeout(1, update_ir_motor_speed);
          }else{
            g_engine_speed = FAULT_DETECTED;
            g_i2c_tx_buffer.push(FAULT_DETECTED);
          }
        }else if(payload >= 2 && payload <= 4){
            g_engine_speed = payload;            
            g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
            timer.setTimeout(1, update_ir_motor_speed);
        }else{
            g_i2c_tx_buffer.push(REJECTED_COMMAND);
        }
        break;
      
      case SET_MODE_OF_OPERATION:
        if(payload == PRI_OPERATION_MODE){
          g_operation_mode = PRI_OPERATION_MODE;
          set_led(DC, OFF, DC);
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
        }else if(payload == SEC_OPERATION_MODE){
          g_operation_mode = SEC_OPERATION_MODE;
          set_led(DC, ON, DC);
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
        }else{
          g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        }
        break;
      
      case SET_MAINT_STATUS:
        if(g_operation_mode == SEC_OPERATION_MODE){
          if(payload == MAINT_STATUS_NORMAL){
            g_main_status_mode = MAINT_STATUS_NORMAL;
            set_led(DC, DC, OFF);
            g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          }else if(payload == MAINT_STATUS_DEBUG){
            g_main_status_mode = MAINT_STATUS_DEBUG;
            set_led(DC, DC, ON);
            g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          }else{
            g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
          }
        }else{
          g_i2c_tx_buffer.push(REJECTED_COMMAND);
        }
        break;        
      
      default:
        g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        break;
    }
  }else if (command != 0xff){
    //recieved a get request, no payload required
    switch(command){
      
      case GET_ENGINE_SPEED:
        g_i2c_tx_buffer.push(g_engine_speed);
        break;
      
      case GET_MODE_OF_OPERATION:
        g_i2c_tx_buffer.push(g_operation_mode);
        break;
      
      case GET_MAINT_STATUS:
        g_i2c_tx_buffer.push(g_main_status_mode);
        break;
      
      case GET_LEGO_PF_CHANNEL:
        g_i2c_tx_buffer.push(LEGO_IR_CHANNEL);
        break;
      
      case GET_LEGO_PF_COLOR:
        g_i2c_tx_buffer.push(LEGO_MOTOR_OUTPUT_BLOCK);
        break;
      
      case RESET:
        g_engine_speed = MOTOR_START_SPEED;
        g_operation_mode = PRI_OPERATION_MODE;
        g_main_status_mode = MAINT_STATUS_NORMAL;
        set_led(ON, OFF, OFF);
        timer.setTimeout(1, update_ir_motor_speed);
        break;
      
      default:
        g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        break;
    }
  }else{
    g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
  }
}

/*
 * Event Handler for processing I2C commands sent to this device
 */
void receiveEvent(int numofbytes)
{  
  while(Wire.available()){
    g_i2c_rx_buffer.push((short) Wire.read());
  }
  process_i2c_request();
}

/*
 * Event Handler for processing an I2C request for data
 */
void requestEvent() {
  if(g_i2c_tx_buffer.isEmpty() != true) {
    while(g_i2c_tx_buffer.isEmpty() != true) {
      Wire.write(g_i2c_tx_buffer.shift());
    }
  }
  else {
    Wire.write(NO_DATA); // Out of data, respond with NO DATA
  }
}


/*
 * Set's LED State
 * 0x00 = OFF = LED off
 * 0x01 = ON = LED on
 * 0x10 = DC = Don't change the state
 */
void set_led(short g, short y, short r) {
  switch(g) {
    case OFF:
      digitalWrite(GREEN_LED, LOW);
      break;

    case ON:
      digitalWrite(GREEN_LED, HIGH);
      break;
  }

  switch(y){
    case OFF:
      digitalWrite(YELLOW_LED, LOW);
      break;

    case ON:
      digitalWrite(YELLOW_LED, HIGH);
      break;
  }

  switch(r) {
    case OFF:
      digitalWrite(RED_LED, LOW);
      break;

    case ON:
      digitalWrite(RED_LED, HIGH);
      break;
  }
}
