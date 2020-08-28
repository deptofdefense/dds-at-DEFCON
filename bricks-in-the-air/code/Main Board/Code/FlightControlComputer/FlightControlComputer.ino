#include <PowerFunctions.h>
#include <Wire.h>
#include <CircularBuffer.h>
#include <SimpleTimer.h>

/**
 *  Project: Bricks in the Air - dds.mil
 *  Title: Flight Control Computer
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
#define I2C_ADDRESS 0x50
#define LEGO_IR_CHANNEL 3 //0=ch1 1=ch2 etc.
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
#define GET_GEAR_POSITION     0x20
#define SET_GEAR_POSITION     0x21
#define GET_MODE_OF_OPERATION 0x30
#define SET_MODE_OF_OPERATION 0x31
#define GET_ALL_STATES        0x35
#define GET_MAINT_STATUS      0x40
#define SET_MAINT_STATUS      0x41
#define SEND_RT_MSG           0x51
#define GET_LEGO_PF_CHANNEL   0x80
#define GET_LEGO_PF_COLOR     0x90
#define RESET                 0xFE
#define POP_SMOKE             0xB5

//Response
#define UNKNOWN_COMMAND       0x33
#define NO_DATA               0xFF
#define DATA_NOT_RETRIEVED    0xDA

#define SUCCESS               0x01
#define FAILURE               0x00

/*
 * Library Instantiations
 */
PowerFunctions pf(LEGO_PF_PIN, LEGO_IR_CHANNEL);   //Setup Lego Power functions pin


/*
 * Globals
 */
short volatile g_operation_mode = PRI_OPERATION_MODE;
short volatile g_main_status_mode = MAINT_STATUS_NORMAL;
boolean volatile g_smoke_popped = false;

// the timer object, used to uncouple the Lego pf call routine from I2C commands
SimpleTimer timer;

CircularBuffer<short,I2C_RX_BUFFER_SIZE> g_i2c_rx_buffer;
CircularBuffer<short,I2C_TX_BUFFER_SIZE> g_i2c_tx_buffer;

/*
 * Setup method to handle I2C Wire setup, LED Pins and Serial output
 */
void setup() {
  int i;  
  Wire.begin(I2C_ADDRESS);      //technically this should be master and thus not have an address
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

  set_led(ON, OFF, OFF);
  
}

/*
 * The main loop of execution for the Engine Control Unit
 */
void loop() {

  timer.run(); 

  if(g_smoke_popped == true){
    pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_FWD7);
    set_led(OFF, DC, DC);
    delay(1000);
    pf.single_pwm(LEGO_MOTOR_OUTPUT_BLOCK, PWM_BRK);
    g_smoke_popped = false;
    set_led(ON, DC, DC);
  }
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
      
      case SET_MODE_OF_OPERATION:
        if(payload == PRI_OPERATION_MODE){
          g_operation_mode = PRI_OPERATION_MODE;
          g_i2c_tx_buffer.push(SUCCESS);
          set_led(DC, OFF, DC);
        }else if(payload == SEC_OPERATION_MODE){
          g_operation_mode = SEC_OPERATION_MODE;
          g_i2c_tx_buffer.push(SUCCESS);
          set_led(DC, ON, DC);
        }else{
          g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        }
        g_i2c_rx_buffer.clear();
        break;

      case SET_MAINT_STATUS:
        if(g_operation_mode == SEC_OPERATION_MODE){
          if(payload == MAINT_STATUS_NORMAL){
            g_main_status_mode = MAINT_STATUS_NORMAL;
            g_i2c_tx_buffer.push(SUCCESS);
            set_led(DC, DC, OFF);
          }else if(payload == MAINT_STATUS_DEBUG){
            g_main_status_mode = MAINT_STATUS_DEBUG;
            g_i2c_tx_buffer.push(SUCCESS);
            set_led(DC, DC, ON);
          }else{
            g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
          }
        }else{
          g_i2c_tx_buffer.push(REJECTED_COMMAND);
        }
        g_i2c_rx_buffer.clear();
        break;

      case POP_SMOKE:
        //Normally logic for this to trigger would reside here, but state conditions are managed 
        //externally to make the virtual reality work with twitch. As such, this command just exits
        //and will execute at face value.
        if(payload == ON){
          g_smoke_popped = true;
          g_i2c_tx_buffer.push(SUCCESS);
        }
        g_i2c_rx_buffer.clear();
        break;
        
      default:
        g_i2c_rx_buffer.clear();
        g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        break;        
    }
  }else if (command != 0xff){
    //recieved a get request, no payload required
    switch(command){
      case GET_ENGINE_SPEED:
      case GET_GEAR_POSITION:
        // Send a fixed response indicating that the chatbot controller has to lookup the correct response
        g_i2c_tx_buffer.push(DATA_NOT_RETRIEVED);
        g_i2c_rx_buffer.clear();
        break;

      case GET_MODE_OF_OPERATION:
        g_i2c_tx_buffer.push(g_operation_mode);
        g_i2c_rx_buffer.clear();
        break;
      
      case GET_MAINT_STATUS:
        g_i2c_tx_buffer.push(g_main_status_mode);
        g_i2c_rx_buffer.clear();
        break;
      
      case GET_LEGO_PF_CHANNEL:
        g_i2c_tx_buffer.push(LEGO_IR_CHANNEL);
        g_i2c_rx_buffer.clear();
        break;
      
      case GET_LEGO_PF_COLOR:
        g_i2c_tx_buffer.push(LEGO_MOTOR_OUTPUT_BLOCK);
        g_i2c_rx_buffer.clear();
        break;

      case RESET:
        g_smoke_popped = false;
        g_operation_mode = PRI_OPERATION_MODE;
        g_main_status_mode = MAINT_STATUS_NORMAL;
        set_led(ON, OFF, OFF);
        g_i2c_rx_buffer.clear();
        g_i2c_tx_buffer.push(SUCCESS);     
        break;
      
      default:
        g_i2c_rx_buffer.clear();
        g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        break;     
    }
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
