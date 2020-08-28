#include <PowerFunctions.h>
#include <Wire.h>
#include <CircularBuffer.h>

/**
 *  Project: Hack The "Airplane" - dds.mil
 *  Title: Engine Control Unit
 *  
 *  Purpose: To expose people to common low level protocols that mimic aviation protocols, specifically 
 *  using I2C as a correlation to 1553.
 *    
 *    
 *  @author Dan Allen
 *  @version 1.0 7/25/19
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
#define ENGINE_I2C_ADDRESS 0x58
#define LEGO_IR_CHANNEL 0 //0=ch1 1=ch2 etc.
#define LEGO_MOTOR_OUTPUT_BLOCK BLUE
#define LEGO_SMOKE_OUTPUT_BLOCK RED
#define SERIAL_BAUD 9600
#define I2C_RX_BUFFER_SIZE 50
#define I2C_TX_BUFFER_SIZE 100
#define SMOKE_LENGTH_MS   10000
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

#define SMOKE_OFF     0x00
#define SMOKE_START   0x01
#define SMOKE_RUNNING 0x02
#define SMOKE_STOP    0x03

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
const String PROGMEM g_no_dbg_command_list = "0x22 0x23 0x63 0xAA";
const String PROGMEM g_dbg_command_list = "0x22 0x23 0x63 0xAA 0x24 0x77";
const String PROGMEM g_ovrd_command_list = "0x22 0x23 0x63 0xAA 0x77 0x99";
const String PROGMEM g_list_cmd_name = "list commands";
const String PROGMEM g_get_status_cmd_name = "get status";
const String PROGMEM g_set_speed_cmd_name = "set speed";
const String PROGMEM g_debug_cmd_name = "set debug mode";
const String PROGMEM g_marco_cmd_name = "marco";
const String PROGMEM g_override_cmd_name = "enable override";
const String PROGMEM g_hbridge_burn_cmd_name = "enable h-bridge burn";
const String PROGMEM g_unknown_cmd_response = "Unknown Command";

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
  

  //Init timers
  g_last_time_ms = millis();    
  g_current_time_ms = millis();

  //run inital state config
  g_smoke_state = SMOKE_OFF;
  g_motor_state = MOTOR_CRUISING_NORMAL;
  g_debug_state = DEBUG_MODE_OFF;
  g_mode_change = true;     

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
  if(g_mode_change == true){   //process new mode of operation
    Serial.print(F("Mode change request to: 0x"));
    Serial.println(g_engine_speed, HEX);
    g_mode_change = false;
    switch(g_motor_state) {

    }
    
    update_ir_motor_speed();
  }

  switch(g_smoke_state){
    case SMOKE_OFF:
      //Just chill here and wait
      break;
      
    case SMOKE_START:
      g_smoke_timer_ms = SMOKE_LENGTH_MS;
      Serial.println(F("SMOKEN!!!"));
      pf.single_pwm(LEGO_SMOKE_OUTPUT_BLOCK, PWM_FWD7);
      g_smoke_state = SMOKE_RUNNING;
      set_led(DC, DC, ON);
      break;

    case SMOKE_RUNNING:
      if(g_smoke_timer_ms == 0) {
          g_smoke_state = SMOKE_STOP;
      }
      break;
      
    case SMOKE_STOP:
      Serial.println(F("Extinguish!!!"));
      pf.single_pwm(LEGO_SMOKE_OUTPUT_BLOCK, PWM_BRK);
      pf.single_pwm(LEGO_SMOKE_OUTPUT_BLOCK, PWM_FLT);
      g_smoke_state = SMOKE_OFF;
      break;
  }
  //Limit loop speed
  //delay(100);
}

/*
 * Parse a string into the I2C buffer to be spit out
 */
void string_to_i2c_buffer(String data) {
  int i;
  for(i=0; i < data.length(); i++) {
    g_i2c_tx_buffer.push(data.charAt(i));
  }
}

/*
 * I2c State machine
 * Needs to be non-blocking and as quick as possible
 */
void process_i2c_request(void) {
  short command_temp;
  if(g_i2c_rx_buffer.isEmpty() != true) {
    //clear any unsent responses
    g_i2c_tx_buffer.clear();
    //read command and pull it out of the buffer
    command_temp = g_i2c_rx_buffer.shift();

    //Non-debug mode
    if(g_debug_enabled == false) {
      Serial.println(F("DBG OFF"));
      switch(command_temp){
        case QUERY_COMMANDS:
          if(g_i2c_rx_buffer.isEmpty() != true) {
            //payload sent, send name of command
            switch(g_i2c_rx_buffer.shift()) {
              case QUERY_COMMANDS:
                Serial.println(F("Query name, Query Command"));
                string_to_i2c_buffer(g_list_cmd_name);
                break;
                
              case GET_ENGINE_STATUS:
                Serial.println(F("Query name, get engine status"));
                string_to_i2c_buffer(g_get_status_cmd_name);
                break;
                
              case SET_ENGINE_SPEED:
                Serial.println(F("Query name, set engine speed"));
                string_to_i2c_buffer(g_set_speed_cmd_name);
                break;

              case SET_DEBUG_MODE:
                Serial.println(F("Query name, set debug mode"));
                string_to_i2c_buffer(g_debug_cmd_name);
                break;

              default:
                Serial.println(F("Queried Unknown command"));
                string_to_i2c_buffer(g_unknown_cmd_response);
                
            }
          }
          else {
            //No payload sent, list commands
            Serial.println(F("Command Received, QUERY_COMMANDS"));
            Serial.println(F("Sending List"));
            string_to_i2c_buffer(g_no_dbg_command_list);
          }

          break;
        
        case GET_ENGINE_STATUS:
          Serial.println(F("Command Received, GET_ENGINE_STATUS"));
          g_i2c_tx_buffer.push(g_engine_speed);
          //string_to_i2c_buffer("hello");
          break;
    
        case SET_ENGINE_SPEED:
          Serial.print(F("Command Received, SET_ENGINE_SPEED : "));
          if(g_i2c_rx_buffer.isEmpty() != true) {
            g_engine_speed = g_i2c_rx_buffer.shift();
            if(g_engine_speed < 2) {
              g_engine_speed = 2;
            }
            if(g_engine_speed > 4) {
              g_engine_speed = 4;
            }
            g_mode_change = true;
            Serial.println(g_engine_speed, HEX);
          }
          //Note, there should be some sanitization here, but maybe not for hacking comp?
          break;
  
        case SET_DEBUG_MODE:
          Serial.print(F("Command Received, SET_DEBUG_MODE : "));
          if(g_i2c_rx_buffer.isEmpty() != true) {
            if(g_i2c_rx_buffer.shift() == 0x01) {
              g_debug_enabled = true;
              Serial.println(F("ON"));
              set_led(OFF, ON, DC);
            }
            else {
              g_debug_enabled = false;
              Serial.println(F("OFF"));
              set_led(ON, OFF, DC);
            }
          }
          
          break;
    
        default:
          Serial.print(F("Received unknown command: "));
          Serial.println(command_temp);
          g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
      }
    }
    else {
    
      //Debug mode enabled
      if(g_debug_enabled == true) {
        Serial.println(F("DBG ON"));
        switch(command_temp){
          case QUERY_COMMANDS:
            if(g_i2c_rx_buffer.isEmpty() != true) {
              //payload sent, send name of command
              switch(g_i2c_rx_buffer.shift()) {
                case QUERY_COMMANDS:
                  Serial.println(F("Query name, Query Command"));
                  string_to_i2c_buffer(g_list_cmd_name);
                  break;
                  
                case GET_ENGINE_STATUS:
                  Serial.println(F("Query name, get engine status"));
                  string_to_i2c_buffer(g_get_status_cmd_name);
                  break;
                  
                case SET_ENGINE_SPEED:
                  Serial.println(F("Query name, set engine speed"));
                  string_to_i2c_buffer(g_set_speed_cmd_name);
                  break;
  
                case SET_DEBUG_MODE:
                  Serial.println(F("Query name, set debug mode"));
                  string_to_i2c_buffer(g_debug_cmd_name);
                  break;

                case MARCO:
                  Serial.println(F("Query name, marco"));
                  string_to_i2c_buffer(g_marco_cmd_name);
                  break;

                case SET_OVERRIDE:
                  Serial.println(F("Query name, Override"));
                  string_to_i2c_buffer(g_override_cmd_name);
                  break;

                case HBRIDGE_BURN:
                  if(g_override_enabled == true) {
                    Serial.println(F("Query name, Override"));
                    string_to_i2c_buffer(g_hbridge_burn_cmd_name);
                  }
                  else {
                    Serial.println(F("Unknown command"));
                    string_to_i2c_buffer(g_unknown_cmd_response);
                  }
                  break;
  
                default:
                  Serial.println(F("Unknown command"));
                  string_to_i2c_buffer(g_unknown_cmd_response);
                  
              }
            }
            else {
              //No payload sent, list commands
              Serial.println(F("Command Received, QUERY_COMMANDS"));
              Serial.println(F("Sending List"));

              
              if(g_override_enabled != true) {
                string_to_i2c_buffer(g_dbg_command_list);
              }
              else
              {
                string_to_i2c_buffer(g_ovrd_command_list);
              }
            }
  
            break;
          
          case GET_ENGINE_STATUS:
            Serial.println(F("Command Received, GET_ENGINE_STATUS"));
            g_i2c_tx_buffer.push(g_engine_speed);
            //string_to_i2c_buffer("hello");
            break;
      
          case SET_ENGINE_SPEED:
            Serial.print(F("Command Received, SET_ENGINE_SPEED : "));
            if(g_i2c_rx_buffer.isEmpty() != true) {
              g_engine_speed = g_i2c_rx_buffer.shift();
              g_mode_change = true;
              Serial.println(g_engine_speed, HEX);
            }
            //Note, there should be some sanitization here, but maybe not for hacking comp?
            break;
    
          case SET_DEBUG_MODE:
            Serial.print(F("Command Received, SET_DEBUG_MODE : "));
            if(g_i2c_rx_buffer.isEmpty() != true) {
              if(g_i2c_rx_buffer.shift() == 0x01) {
                g_debug_enabled = true;
                set_led(OFF, ON, DC);
                Serial.println(F("ON"));
              }
              else {
                g_debug_enabled = false;
                set_led(ON, OFF, DC);
                Serial.println(F("OFF"));
              }
            }
            
            break;

          case MARCO:
            Serial.print(F("Command Received, Marco"));
            string_to_i2c_buffer("Polo");
            break;

          case SET_OVERRIDE:
            Serial.print(F("Command Received, Override :"));
            if(g_i2c_rx_buffer.isEmpty() != true) {
              if(g_i2c_rx_buffer.shift() == 0x01) {
                g_override_enabled = true;
                Serial.println(F("ON"));
              }
              else {
                g_override_enabled = false;
                Serial.println(F("OFF"));
              }
            }
            break;

          case HBRIDGE_BURN:
            if(g_override_enabled == true) {
              Serial.print(F("Command Received, BURN!!!"));
              g_smoke_state = SMOKE_START;
            }
            break;
      
          default:
            Serial.print(F("Received unknown command: "));
            Serial.println(command_temp);
            g_i2c_tx_buffer.push(UNKNOWN_COMMAND);
        }

        
      }
    }
    g_i2c_rx_buffer.clear(); //flush buffer after processing  
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
