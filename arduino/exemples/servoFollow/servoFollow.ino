#include <PID_v1.h>

#include <Servo.h>

#include "CmdMessenger.h"

enum
{
    targetData,
    servoDirection,
    error,
};

const int BAUD_RATE = 9600;
CmdMessenger c = CmdMessenger(Serial,',',';','/');

float objectDirection;
float servoPosition;
float setPoint = 0;
float Kp=20, Ki=1, Kd=1;
PID pid(&objectDirection, &servoPosition, &setPoint, Kp, Ki, Kd, DIRECT);

Servo servo;


void onObjDetected(void)
{
  objectDirection = c.readBinArg<float>();
  
  int value2 = c.readBinArg<int>();
  int value3 = c.readBinArg<int>();
  int value4 = c.readBinArg<int>();
  int value5 = c.readBinArg<int>();

  pid.compute();
  
  c.sendCmdStart(servoDirection);
  c.sendCmdBinArg<float>(servoPosition);
  c.sendCmdEnd();
}

void onUnknownCommand(void)
{
  c.sendCmd(error, "Comando sem handler definido");
}

void attachHandlers(void)
{
  c.attach(targetData, onObjDetected);
  c.attach(onUnknownCommand);
}

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(BAUD_RATE);
  attachHandlers();
  pid.setOutputLimits(0, 255);
  pid.setMode(AUTOMATIC);
  pid.setSampleTime(0);
  servo.attach(9);
}

bool state = false;
void loop()
{
  c.feedinSerialData();
  //servo.write(servoPosition);
}
