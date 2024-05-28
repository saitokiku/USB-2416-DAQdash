// Define the pin where the signal will be output
const int signalPin = 9; // PWM pin on Arduino

unsigned long waveChangeTime = 0;
int waveType = 0;

void setup() {
  pinMode(signalPin, OUTPUT);
}

void loop() {
  // Change waveform type every 5 seconds
  if (millis() - waveChangeTime > 5000) {
    waveChangeTime = millis();
    waveType = (waveType + 1) % 2; // Only two wave types
  }

  if (waveType == 0) {
    generateSquareWave();
  } else {
    generateSineWave();
  }
}

void generateSquareWave() {
  for (int i = 0; i < 50; i++) {
    analogWrite(signalPin, 255); // High state
    delay(10); // High duration
    analogWrite(signalPin, 0); // Low state
    delay(10); // Low duration
  }
}

void generateSineWave() {
  for (int i = 0; i < 360; i++) {
    float rad = DEG_TO_RAD * i;
    int sineValue = 127.5 + 127.5 * sin(rad); // Scale sine to 0-255
    analogWrite(signalPin, sineValue);
    delay(2); // Adjust delay for frequency
  }
}
