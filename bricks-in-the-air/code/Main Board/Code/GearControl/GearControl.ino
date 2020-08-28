#include <PowerFunctions.h>
#include <Wire.h>
#include <CircularBuffer.h>
#include <SimpleTimer.h>

/**
 *  Project: Bricks in the Air - dds.mil
 *  Title: Landing Gear Control Computer
 *  
 *  Purpose: To expose people to common low level protocols that mimic aviation protocols, specifically 
 *  using I2C as a correlation to 1553.
 *  
 *  LED usage:
 *    Green: Gear is down and locked
 *    Yellow: Gear is in transit
 *    Red: Gear is retracted
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
#define I2C_ADDRESS 0x60
#define LEGO_IR_CHANNEL 0 //0=ch1 1=ch2 etc.
#define LEGO_MOTOR_OUTPUT_BLOCK 0x01 // 0x00 RED, 0x01 BLUE
#define SERIAL_BAUD 9600
#define I2C_RX_BUFFER_SIZE 100
#define I2C_TX_BUFFER_SIZE 200
#define STARTUP_LED_SPEED_MS  100

#define GEAR_RETRACT_DELAY 5000  //Gear up/down will need to be tuned per Lego model
#define GEAR_EXTEND_DELAY 5000
const short GEAR_EXTEND_DIRECTION = PWM_REV3;
const short GEAR_RETRACT_DIRECTION = PWM_FWD3;
const short GEAR_STOP_DIRECTION = PWM_BRK;

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

#define GEAR_EXTENDED 0x00
#define GEAR_RETRACTED 0x01
#define GEAR_IN_TRANSIT 0x02

#define PRI_OPERATION_MODE 0x00
#define SEC_OPERATION_MODE  0x01
#define MAINT_STATUS_NORMAL 0x00
#define MAINT_STATUS_DEBUG 0x01

/*
 * I2C Comms Definitions
 */
//Commands
#define GET_GEAR_POS 0x20
#define SET_GEAR_POS 0x21
#define GET_MODE_OF_OPERTION 0x30
#define SET_MODE_OF_OPERTION 0x31
#define GET_MAINT_STATUS 0x40
#define SET_MAINT_STATUS 0x41
#define GET_LEGO_PF_CHANNEL 0x80
#define GET_LEGO_PF_COLOR 0x90
#define RESET 0xFE

//Response
#define UNKNOWN_COMMAND   0x33
#define NO_DATA           0xFF

#define REJECTED_COMMAND 0xDE
#define ACCEPTED_COMMAND 0x01
#define FAULT_DETECTED   0xDA

/*
 * Library Instantiations
 */
PowerFunctions pf(LEGO_PF_PIN, LEGO_IR_CHANNEL);   //Setup Lego Power functions pin


/*
 * Globals
 */
short volatile g_gear_position = GEAR_RETRACTED;
short volatile g_pri_operation_mode = PRI_OPERATION_MODE;
short volatile g_main_status_mode = MAINT_STATUS_NORMAL;
boolean volatile g_mode_change = false;
boolean volatile g_lower_gear = false;
boolean volatile g_raise_gear = false;

// the timer object
SimpleTimer timer;

 
CircularBuffer<short,I2C_RX_BUFFER_SIZE> g_i2c_rx_buffer;
CircularBuffer<short,I2C_TX_BUFFER_SIZE> g_i2c_tx_buffer;

/*
 * The function the timer calls to the stop motion of the gear motor
 */
void stop_motor(){
  pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, GEAR_STOP_DIRECTION);
  if(g_lower_gear == true){
    g_gear_position = GEAR_EXTENDED;
    g_lower_gear = false;
    set_led(ON, OFF, OFF);
  }else if(g_raise_gear == true){
    g_gear_position = GEAR_RETRACTED;
    g_raise_gear = false;
    set_led(OFF, OFF, ON);
  }  
}

/*
 * Setup method to handle I2C Wire setup, LED Pins and Serial output
 */
void setup() {
  int i;  
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent); // register event handler for recieve
  Wire.onRequest(requestEvent); // register event handler for request

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  
  Serial.begin(SERIAL_BAUD);    // start serial for output debugging
  Serial.println(F("Main Engine Control Unit is online, ready for tasking"));
  
  //run inital state config
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

  // Gear is normally retracted at startup
  set_led(OFF, OFF, ON);
  
}

/*
 * The main loop of execution for the Engine Control Unit
 */
void loop() {
  timer.run();  
}


/*
 * I2c State machine
 * Needs to be non-blocking and as quick as possible
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
      case SET_GEAR_POS:
        if(payload == g_gear_position){
          //nothing to do, already in the desired state
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          break;
        }else if(g_gear_position == GEAR_RETRACTED && payload == GEAR_EXTENDED){
          set_led(OFF, ON, OFF);
          //requesting a gear change from retracted to lowered
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          delay(1);
          g_gear_position = GEAR_IN_TRANSIT;
          g_lower_gear = true;
          pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, GEAR_EXTEND_DIRECTION);          
          timer.setTimeout(GEAR_EXTEND_DELAY, stop_motor);
        }else if(g_gear_position == GEAR_EXTENDED && payload == GEAR_RETRACTED){
          //requesting a gear change from lowered to retracted
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          delay(1);
          set_led(OFF, ON, OFF);
          g_gear_position = GEAR_IN_TRANSIT;
          g_raise_gear = true;
          pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, GEAR_RETRACT_DIRECTION);          
          timer.setTimeout(GEAR_RETRACT_DELAY, stop_motor);
        }else{
          //gear is probably in transit... do nothing
          //maybe put an easter egg here.. it would be timing dependent to execute.
          g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
          break;
        }
        
        break;  
            
      case SET_MODE_OF_OPERTION:
        if(payload == PRI_OPERATION_MODE){
          g_pri_operation_mode = PRI_OPERATION_MODE;
          set_led(DC, OFF, DC);
        }else if(payload == SEC_OPERATION_MODE){
          g_pri_operation_mode = SEC_OPERATION_MODE;
          set_led(DC, ON, DC);
        }
        g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
        break;   
             
      case SET_MAINT_STATUS:
        if(payload == MAINT_STATUS_NORMAL){
          g_main_status_mode = MAINT_STATUS_NORMAL;
          set_led(DC, DC, OFF);
        }else if(payload == MAINT_STATUS_DEBUG){
          g_main_status_mode = MAINT_STATUS_DEBUG;
          set_led(DC, DC, ON);
        }
        g_i2c_tx_buffer.push(ACCEPTED_COMMAND);
        break;
        
      default:
        g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        break;
       
    }    
  }else if(command != 0xff){
    //recieved a get request, no payload required
    switch(command){
      case GET_GEAR_POS:
        g_i2c_tx_buffer.push(g_gear_position);        
        break;
      case GET_MODE_OF_OPERTION:
        g_i2c_tx_buffer.push(g_pri_operation_mode);        
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
      // Reset all local variables EXCEPT the position of the GEAR (i.e. up or down)
        g_i2c_tx_buffer.clear();
        g_i2c_rx_buffer.clear();
        g_pri_operation_mode = PRI_OPERATION_MODE;
        g_main_status_mode = MAINT_STATUS_NORMAL;

        // determine if gear is in transit.. if so... finish first
        if (g_gear_position == GEAR_IN_TRANSIT){
          // delay at least lenght of time for full transit
          delay(GEAR_RETRACT_DELAY);
          if(g_lower_gear){
            g_mode_change = false;
            g_lower_gear = false;
            g_raise_gear = false;
            g_gear_position = GEAR_EXTENDED;
          }else if(g_raise_gear){
            g_mode_change = false;
            g_lower_gear = false;
            g_raise_gear = false;
            g_gear_position = GEAR_RETRACTED;
          }
        }
        
        if(g_gear_position == GEAR_RETRACTED){
          set_led(OFF, OFF, ON);
        }else if(g_gear_position == GEAR_EXTENDED){
          set_led(ON, OFF, OFF);
        }
        
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
 * NOTE: I don't like accessing the response in this inturrupt,
 * but I2C needs an imeediate response.
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
    case 0x00:
      digitalWrite(GREEN_LED, LOW);
      break;

    case 0x01:
      digitalWrite(GREEN_LED, HIGH);
      break;
  }

  switch(y){
    case 0x00:
      digitalWrite(YELLOW_LED, LOW);
      break;

    case 0x01:
      digitalWrite(YELLOW_LED, HIGH);
      break;
  }

  switch(r) {
    case 0x00:
      digitalWrite(RED_LED, LOW);
      break;

    case 0x01:
      digitalWrite(RED_LED, HIGH);
      break;
  }
}
