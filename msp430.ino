
double kp = 4;  // PID P constant
double ki = 0.005; // PID I constant
double kd = 0.1;  // PID D constant
double lastError2=0; // previous PID error
unsigned long previousTime=0; //previous time
double cumError=0; // PID error over time (integral)
double input; // ADC value 
float setPoint = 0; // PID input value

void setup() {
  pinMode(A0, OUTPUT); // PID regulated output pin
  Serial.begin(9600); 
}

void loop() {
  input=analogRead(A3); // reading capacitor voltage
    if (Serial.available() > 0) {                       //reading incoming serial data, range 0-255
        float serialValue=Serial.read();
          if (serialValue>=0 && serialValue<=255) {
            setPoint=serialValue;
            setPoint=map(setPoint, 0, 255, 0, 4095);
          }                                            //-------------------------------------------
    }
  analogWrite(A0, computePID(input,setPoint,kp,ki,kd));  //write computed PID output value to pin 
  Serial.println(adcToVoltage(input,3.3,12));            //send on serial ADC value in volts (capacitor voltage)
  delay(1);
}

double adcToVoltage(double adcValue, float adcVoltage, float adcBits) {   //function that coverts ADC value to volts
  double conversionConstant = adcVoltage/pow(2,adcBits);
  return adcValue * conversionConstant;
  }                                                                       //-----------------------------------------

double computePID(double inp, double setPoint, double kp, double ki, double kd){  // PID controller
  unsigned long currentTime;
  double elapsedTime;
  double error;
  double rateError; 

  currentTime = millis();                //get current time
  elapsedTime = (double)(currentTime - previousTime);        //compute time elapsed from previous computation      
  error = setPoint - inp;                                // determine error
  cumError += error * elapsedTime;                // compute integral
  rateError = (error - lastError2)/elapsedTime;   // compute derivative
  double out = kp*error + ki*cumError + kd*rateError;                //PID output               
  lastError2 = error;                                //remember current error
  previousTime = currentTime;                        //remember current time
    if (out<0) {
      out=0;
    } 
  return out;                                        //have function return the PID output
}                                                                       //---------------------------------------------