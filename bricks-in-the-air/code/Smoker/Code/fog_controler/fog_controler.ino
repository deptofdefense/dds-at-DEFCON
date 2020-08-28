/*
  Fog Controller

  This program provides control logic for the fogger. Most importantly this keeps the figger from
  running too long and overheating. It also uses the built in eeprom to save setting for pump rate,
  fog rate, max on time, min cooldown time. These settings can be adjusted via serial.
  
*/
#include <EEPROM.h>

//Pin settings (note Pump and Fog pins PWM enabled pins!)
#define PUMP_PWM_PIN    10
#define FOG_PWM_PIN     11
#define TRIGGER_PIN     9

//Default level and timing settings
#define DEFAULT_PUMP    255
#define MIN_PUMP        0
#define MAX_PUMP        255

#define DEFAULT_FOG     255
#define MIN_FOG         0
#define MAX_FOG         255

#define DEFAULT_RUN     15
#define MIN_RUN         0
#define MAX_RUN         255

#define DEFAULT_COOL    60
#define MIN_COOL        0
#define MAX_COOL        255

//EEPROM memory mapping
#define EEPROM_INIT_CHECK_ADDRESS 0x00
#define EEPROM_PUMP_ADDRESS       0x01
#define EEPROM_FOG_ADDRESS        0x02
#define EEPROM_RUN_ADDRESS        0x03
#define EEPROM_COOL_ADDRESS       0x04
#define EEPROM_INIT_CHECK_VALUE   0xAA

//Fogger state machine states
#define FOG_OFF       0x01
#define FOG_RUNNING   0x02
#define FOG_COOLDOWN  0x03


//Global variables
//Holds current system setting
int g_pump_speed = 0;
int g_fog_speed = 0;
int g_run_time = 0;
int g_cool_time = 0;

//Timer variables
volatile unsigned long g_timer_current_time = 0;
volatile unsigned long g_timer_previous_mark = 0;
volatile unsigned long g_fog_running_timer = 0;
volatile unsigned long g_fog_cooldown_timer = 0;

//Used to track UART triggering mode
volatile bool g_manual_trigger = 0;

//Fogger state machine variable
volatile int g_fogger_state = FOG_OFF;

//Function Prototypes
void print_instructions(void);
void print_default_settings(void);
void print_current_settings(void);
void eeprom_init_check(void);
void reset_defaults(void);
void service_serial(void);
void service_pwm(void);
void service_timers(void);

//Setup Routine, runs once on startup
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  
  //Set pin modes and initial states
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  pinMode(PUMP_PWM_PIN, OUTPUT);
  pinMode(FOG_PWM_PIN, OUTPUT);
  pinMode(TRIGGER_PIN, INPUT);

  //Run EEPROM memory initialization
  eeprom_init_check();

  //Print welcome message to UART
  print_instructions();
}

// the loop routine runs over and over again forever:
void loop() {
  //Manage timers
  service_timers();
  
  //Check for serial communication
  service_serial();
  
  //check for trigger and set PWM's 
  service_pwm();
}


// Decrements system timers
void service_timers(void)
{
  unsigned long delta = 0;
  //Update current time
  g_timer_current_time = millis();

  //Check for wrap-around of time (happends about every 49.7 days)
  if(g_timer_previous_mark < g_timer_current_time)
  {
    //timer has not rolled over, simply subtract times
    delta = g_timer_current_time - g_timer_previous_mark;
  }
  else
  {
    //timer has rolled over, calculate delta past rollover point
    delta = (4294967295 - g_timer_previous_mark) + g_timer_current_time;
  }

  //Replace last saved time with current time
  g_timer_previous_mark = g_timer_current_time;

  /* Proccess each countdown timer */
  if(g_fog_running_timer > delta)
  {
    g_fog_running_timer = g_fog_running_timer - delta;
  }
  else
  {
    g_fog_running_timer = 0;
  }

  if(g_fog_cooldown_timer > delta)
  {
    g_fog_cooldown_timer = g_fog_cooldown_timer - delta;
  }
  else
  {
    g_fog_cooldown_timer = 0;
  }
  
}


//Run state machine that controls the foger output levels
void service_pwm(void)
{
  switch(g_fogger_state)
  {
    case FOG_OFF:
      //If either triggered by UART or a HIGH on trigger pin, run
      if((g_manual_trigger == true) ||
         (digitalRead(TRIGGER_PIN) == HIGH))
         {
            //Set the run time
            reset_run_timer();

            //Reset trigger variable for uart
            g_manual_trigger = false;

            //Print state message to UART
            Serial.println("Fogger Triggered");
            
            //Transititon to next state
            g_fogger_state = FOG_RUNNING;
         }
    break;

    case FOG_RUNNING:
      if(g_fog_running_timer > 0)
      {
        //While running, continually update PWM and pin states
        analogWrite(FOG_PWM_PIN, (g_fog_speed));
        analogWrite(PUMP_PWM_PIN, (g_pump_speed));
        digitalWrite(LED_BUILTIN, HIGH);
      }
      else
      {
        //If the timer is up, shut everything off
        analogWrite(FOG_PWM_PIN, 0);
        analogWrite(PUMP_PWM_PIN, 0);
        digitalWrite(LED_BUILTIN, LOW);

        //Reset cooldown timer
        reset_cool_timer();

        //Print state message to UART
        Serial.println("Fogger entering cooldown");

        //Transiiton to next state
        g_fogger_state = FOG_COOLDOWN;
      }

    break;

    case FOG_COOLDOWN:
      //Wait here until cooldown timer has elapsed
      if(g_fog_cooldown_timer == 0)
      {
        //Print state message to UART
        Serial.println("Fogger reset and ready");

        //Transition to next state
        g_fogger_state = FOG_OFF;
      }
    break;
    
  }
}

//Helper function to reset run timer
void reset_run_timer(void)
{
    g_fog_running_timer = 1000 * g_run_time;
}

//Helper function to reset cooldown timer
void reset_cool_timer(void)
{
    g_fog_cooldown_timer = 1000 * g_cool_time;
}

//Manage serial interface and parse input commands
void service_serial(void)
{
  char temp_byte=0;
  int  temp_setting=0;
  // if there's any serial available, read it:
  while (Serial.available() > 0) 
  {
    switch(Serial.read())
    {
      case 'p':
      case 'P':
       
        temp_setting = Serial.parseInt();
        if (Serial.read() == '\n')
        {
          Serial.print("Setting pump level to: ");
          temp_setting = constrain(temp_setting, MIN_PUMP, MAX_PUMP);
          Serial.println(temp_setting);

          //Set pump speed and record setting in EEPROM
          g_pump_speed = temp_setting;
          EEPROM.write(EEPROM_PUMP_ADDRESS, (char*)temp_setting);
        }
      break;

      case 'f':
      case 'F':
       
        temp_setting = Serial.parseInt();
        if (Serial.read() == '\n')
        {
          Serial.print("Setting fog level to: ");
          temp_setting = constrain(temp_setting, MIN_FOG, MAX_FOG);
          Serial.println(temp_setting);

          //Set fog level and record setting in EEPROM
          g_fog_speed = temp_setting;
          EEPROM.write(EEPROM_FOG_ADDRESS, (char*)temp_setting);
        }
      break;

      case 'r':
      case 'R':
       
        temp_setting = Serial.parseInt();
        if (Serial.read() == '\n')
        {
          Serial.print("Setting Max run time in seconds to: ");
          temp_setting = constrain(temp_setting, MIN_RUN, MAX_RUN);
          Serial.println(temp_setting);

          //Set max runtime and write to EEPROM
          g_run_time = temp_setting;
          EEPROM.write(EEPROM_RUN_ADDRESS, (char*)temp_setting);
        }
      break;

      case 'c':
      case 'C':
       
        temp_setting = Serial.parseInt();
        if (Serial.read() == '\n')
        {
          Serial.print("Setting Min cooldown time in seconds to: ");
          temp_setting = constrain(temp_setting, MIN_COOL, MAX_COOL);
          Serial.println(temp_setting);

          //Set min cooldown and write to EEPROM
          g_cool_time = temp_setting;
          EEPROM.write(EEPROM_COOL_ADDRESS, (char*)temp_setting);
        }
      break;

      case 'd':
      case 'D':
        delay(1); //wait for next char to come in
        if (Serial.read() == '\n')
        {
          Serial.print("Resetting all settings to default");

          //Call helper function to reset all defaults in system
          //Also writes to EEPROM
          reset_defaults();
        }
      break;

      case 't':
      case 'T':
        delay(1); //wait for next char to come in
        if (Serial.read() == '\n')
        {
          Serial.println("Manually Triggering Fogger");

          //Set global to indicate to manually trigger fogger
          g_manual_trigger = true;
        }
      break;


      default:
          Serial.println("Unknown Command");
          print_instructions();

          delay(100);        // Wait for all the other chars to come in
          //Empty buffer
          while (Serial.available() > 0)
          {
            Serial.read();
          }
    }
  }
  delay(1);        // delay in between reads for stability
}

//Helper function to print the instructions
void print_instructions(void)
{
  Serial.println(" ");
  Serial.println("Instructions:");
  Serial.println("The first letter is the command");
  Serial.println("The numbers following the letter (if applicable) is the setting");
  Serial.println("For example p50 will set the pump to 50% duty");
  Serial.println("Warning, it's up to you to make sure you supply adiquate air");
  Serial.println("for the fog level. You also need to make sure you don't run ");
  Serial.println("the fogger too long or you can cause a hazardus condition. ");
  Serial.println("Make sure you allow enough cooldown time also.");
  print_pin_config();
  print_default_settings();
  print_current_settings();
  Serial.println("---------------------------------------------------------------");
  Serial.print("P### - Set pump speed %     (range "); Serial.print(MIN_PUMP); Serial.print("-"); Serial.print(MAX_PUMP); Serial.println(")");
  Serial.print("F### - Set fog level %      (range "); Serial.print(MIN_FOG); Serial.print("-"); Serial.print(MAX_FOG); Serial.println(")");
  Serial.print("R### - Max Run Time Seconds (range "); Serial.print(MIN_RUN); Serial.print("-"); Serial.print(MAX_RUN); Serial.println(")");
  Serial.print("C### - Set Cooldown time    (range "); Serial.print(MIN_COOL); Serial.print("-"); Serial.print(MAX_COOL); Serial.println(")");
  Serial.println("D    - Reset all to default");
  Serial.println("T    - Manually Trigger Fogger");

}

//Helper function to print the pin configuration
void print_pin_config(void)
{
  Serial.print("Fogger control pin is : ");
  Serial.println(FOG_PWM_PIN);

  Serial.print("Pump control pin is : ");
  Serial.println(PUMP_PWM_PIN);

  Serial.print("Trigger pin is : ");
  Serial.println(TRIGGER_PIN);
}

//Helper function to print the default settings
void print_default_settings(void)
{
  Serial.println(" ");
  Serial.println("Default Settings:");
  Serial.print("Pump % = ");
  Serial.println(DEFAULT_PUMP);
  Serial.print("Fog % = ");
  Serial.println(DEFAULT_FOG);
  Serial.print("Run time [s] = ");
  Serial.println(DEFAULT_RUN);
  Serial.print("Cooldown time [s] = ");
  Serial.println(DEFAULT_COOL);
}

//Helper function to print the current settings
void print_current_settings(void)
{
  Serial.println(" ");
  Serial.println("Current Settings:");
  Serial.print("Pump % = ");
  Serial.println(g_pump_speed);
  Serial.print("Fog % = ");
  Serial.println(g_fog_speed);
  Serial.print("Run time [s] = ");
  Serial.println(g_run_time);
  Serial.print("Cooldown time [s] = ");
  Serial.println(g_cool_time);
}

//Checks the EEPROM to see if it has valid data in it
//If so it populates the system with the saved settings
//If not it uses system defaults and writes them to EEPROM
void eeprom_init_check(void)
{
  char init_byte = EEPROM.read(EEPROM_INIT_CHECK_ADDRESS);

  if(EEPROM.read(EEPROM_INIT_CHECK_ADDRESS) == EEPROM_INIT_CHECK_VALUE)
  {
    Serial.println("Saved State Found, populating settings");
    //Should be initalized, populate globals
    g_pump_speed = constrain(EEPROM.read(EEPROM_PUMP_ADDRESS), MIN_PUMP, MAX_PUMP);
    g_fog_speed = constrain(EEPROM.read(EEPROM_FOG_ADDRESS), MIN_FOG, MAX_FOG);
    g_run_time = constrain(EEPROM.read(EEPROM_RUN_ADDRESS), MIN_RUN, MAX_RUN);
    g_cool_time = constrain(EEPROM.read(EEPROM_COOL_ADDRESS), MIN_COOL, MAX_COOL);
  }
  else
  {
    //EEPROM not initalized, populate and save defaults
    Serial.println("Saved State Not Found, populating defaults");
    
    reset_defaults();
  }
}

//Helper function to set the system values to defaults
void reset_defaults(void)
{
    g_pump_speed = DEFAULT_PUMP;
    EEPROM.write(EEPROM_PUMP_ADDRESS, DEFAULT_PUMP);

    g_fog_speed = DEFAULT_FOG;
    EEPROM.write(EEPROM_FOG_ADDRESS, DEFAULT_FOG);

    g_run_time = DEFAULT_RUN;
    EEPROM.write(EEPROM_RUN_ADDRESS, DEFAULT_RUN);

    g_cool_time = DEFAULT_COOL;
    EEPROM.write(EEPROM_COOL_ADDRESS, DEFAULT_COOL);

    EEPROM.write(EEPROM_INIT_CHECK_ADDRESS, EEPROM_INIT_CHECK_VALUE);
}
