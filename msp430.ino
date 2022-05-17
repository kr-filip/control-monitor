
double kp = 4;
double ki = 0.005;
double kd = 0.1;
double out=0;
double lastError2=0;
unsigned long previousTime=0;
double cumError=0; 
double input;
float setPoint = 0;

void setup() {
  pinMode(A0, OUTPUT);
  Serial.begin(9600); 
}

void loop() {
  input=analogRead(A3);
    if (Serial.available() > 0) {
        float serialValue=Serial.read();
          if (serialValue>=0 && serialValue<=255) {
            setPoint=serialValue;
            setPoint=map(setPoint, 0, 255, 0, 4095);
          }        
    }
  out = computePID(input,setPoint,kp,ki,kd);  
  analogWrite(A0, out);   
  Serial.println(adcToVoltage(input,3.3,12));
  Serial.println(setPoint);
  delay(1);
}

double adcToVoltage(double adcValue, float adcVoltage, float adcBits) {
  double conversionConstant = adcVoltage/pow(2,adcBits);
  return adcValue * conversionConstant;
  }

double computePID(double inp, double setPoint, double kp, double ki, double kd){ 
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
}