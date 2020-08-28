#include <PowerFunctions.h>
#include <Wire.h>
#include <CircularBuffer.h>

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
 *    https://github.com/jurriaan/Arduino-PowerFunctions *    
 */

/*
 * General Config Definitions
 */
#define I2C_ADDRESS 0x50
#define I2C_ENGINE_ADDRESS 0x58
#define LEGO_IR_CHANNEL 0 //0=ch1 1=ch2 etc.
#define LEGO_MOTOR_OUTPUT_BLOCK BLUE
#define LEGO_SMOKE_OUTPUT_BLOCK RED
#define SERIAL_BAUD 9600
#define I2C_RX_BUFFER_SIZE 50
#define I2C_TX_BUFFER_SIZE 100
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

#define MOTOR_CRUISING_NORMAL 0x00

#define DEBUG_MODE_ON   0xAA
#define DEBUG_MODE_OFF  0x00


/*
 * I2C Comms Definitions
 */
//Commands
#define GET_ENGINE_STATUS 0x22
#define SET_ENGINE_SPEED  0x23
#define MARCO             0x24
#define QUERY_COMMANDS    0x63
#define SMOKEN            0x42
#define SET_DEBUG_MODE    0xAA
#define SET_OVERRIDE      0x77
#define HBRIDGE_BURN      0x99


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
short volatile g_engine_speed = 0;
short volatile g_smoke_state = 0;
short volatile g_motor_state = 0;
short volatile g_debug_state = 0;
boolean volatile g_mode_change = false;
boolean volatile g_debug_enabled = false;
boolean volatile g_override_enabled = false;

//Timers
unsigned long volatile g_last_time_ms = 0;
unsigned long volatile g_current_time_ms =0;
unsigned long volatile g_smoke_timer_ms = 0;



CircularBuffer<short,I2C_RX_BUFFER_SIZE> g_i2c_rx_buffer;
CircularBuffer<short,I2C_TX_BUFFER_SIZE> g_i2c_tx_buffer;

/*
 * Strings
 */
const char g_no_dbg_command_list[] PROGMEM = {"0x22 0x23 0x63 0xAA"};
const char g_dbg_command_list[] PROGMEM = {"0x22 0x23 0x63 0xAA 0x24 0x77"};
const char g_ovrd_command_list[] PROGMEM = {"0x22 0x23 0x63 0xAA 0x77 0x99"};
const char g_list_cmd_name[] PROGMEM = {"list commands"};
const char g_get_status_cmd_name[] PROGMEM = {"get status"};
const char g_set_speed_cmd_name[] PROGMEM = {"set speed"};
const char g_debug_cmd_name[] PROGMEM = {"set debug mode"};
const char g_marco_cmd_name[] PROGMEM = {"marco"};
const char g_override_cmd_name[] PROGMEM = {"enable override"};
const char g_hbridge_burn_cmd_name[] PROGMEM  = {"enable h-bridge burn"};
const char g_unknown_cmd_response[] PROGMEM = {"Unknown Command"};

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
  

  //Init timers
  g_last_time_ms = millis();    
  g_current_time_ms = millis();

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
  service_ir_comms();
  service_timers();
  
}

/*
 * Allows for non-blocking timers
 * Note, the timer accuraccy is no better than 1ms and only as good as
 * how often the service_timers function get's called. A better way to
 * do this is run a decrementer in a timer inturrupt but Arduino framework
 * makes that difficult.
 */
 void service_timers() {
  unsigned long delta = 0;
  g_current_time_ms = millis();
  delta = g_current_time_ms - g_last_time_ms;
  g_last_time_ms = g_current_time_ms;
  
  //decrement individual timers
  decrement_timer(&g_smoke_timer_ms, &delta);
 }

/*
 * Helper function to decrement timers
 */
 void decrement_timer(unsigned long volatile *timer, unsigned long *delta) {
  if(*timer > *delta) {
    *timer = *timer - *delta;
  }
  else {
    *timer = 0;
  }
 }


/*
 * Manages IR comms interface
 */
void service_ir_comms() {

}

/*
 * Parse a string into the I2C buffer to be spit out
 */
void string_to_i2c_buffer(String data) {
  int i;
  for(i=0; i < data.length(); i++) {
    g_i2c_tx_buffer.push(data.charAt(i));
  }
  //terminate buffer with newline to know when finished
  g_i2c_tx_buffer.push('\n');
}

/*
 * I2c State machine
 * Needs to be non-blocking and as quick as possible
 */
void process_i2c_request(void) {
  
}


/*
 * Event Handler for processing I2C commands sent to this device
 * NOTE: I don't like accessing the response in this inturrupt,
 * but I2C needs an imeediate response.
 */
void receiveEvent(int numofbytes)
{  
  
}

/*
 * Event Handler for processing an I2C request for data
 */
void requestEvent() {
 
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

/*
 * Update motor speed by sending IR command
 */
 void update_ir_motor_speed(void) {
  
 }
