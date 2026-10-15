#include <Adafruit_PWMServoDriver.h>
#include <MS5837.h>
#include <WebServer_WT32_ETH01.h>
#include <WiFiUdp.h>
#include <Wire.h>

/* ===================== RED ===================== */
IPAddress myIP(192, 168, 1, 21);
IPAddress myGW(192, 168, 1, 1);
IPAddress mySN(255, 255, 255, 0);
IPAddress myDNS(8, 8, 8, 8);

/* ===================== UDP ===================== */
WiFiUDP udp;
const int UDP_PORT = 8888;
char packetBuffer[64];

WiFiUDP udpSend;
const int UDP_SEND_PORT = 8889;
IPAddress hostIP;

/* ===================== I2C ===================== */
#define I2C_SDA 32
#define I2C_SCL 33

/* ===================== PCA9685 ===================== */
Adafruit_PWMServoDriver pca9685(0x40);

#define PWM_FREQ 50 // Corregido a 50 Hz estándar para ESCs
#define OSC_FREQ 26000000
#define NUM_MOTORS 8

#define ESC_NEUTRAL_US 1500
#define ESC_MIN_US 1100
#define ESC_MAX_US 1900

bool bar = true;

// Variables sensor MS5837
float pressure, temperature, depth, altitude = 0;
MS5837 bar02;

// ===================== WATCHDOG Y TEMPORIZADORES =====================
unsigned long lastPacketTime = 0;
const unsigned long WATCHDOG_MS = 2000; // Reducido a 2 segundos por seguridad
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 100; // Enviar telemetría a 10 Hz

/* ===================== UTILS ===================== */
const uint8_t PWM_CHANNEL[NUM_MOTORS] = {14, 13, 12, 11, 10, 9, 8, 6};

void setMotors(uint16_t pwms[NUM_MOTORS]) {
  for (int i = 0; i < NUM_MOTORS; i++) {
    pca9685.writeMicroseconds(PWM_CHANNEL[i], pwms[i]);
  }
}

void stopAllMotors() {
  uint16_t neutralPwms[NUM_MOTORS];
  for (int i = 0; i < NUM_MOTORS; i++) {
    neutralPwms[i] = ESC_NEUTRAL_US;
  }
  setMotors(neutralPwms);
}

bool parsePacket(const char *buf, uint16_t out[NUM_MOTORS]) {
  char tmp[64];
  strncpy(tmp, buf, sizeof(tmp) - 1);
  tmp[sizeof(tmp) - 1] = '\0';

  int count = 0;
  char *token = strtok(tmp, ";");

  while (token != NULL && count < NUM_MOTORS) {
    int val = atoi(token);
    if (val < ESC_MIN_US || val > ESC_MAX_US)
      return false;
    out[count++] = (uint16_t)val;
    token = strtok(NULL, ";");
  }

  return (count == NUM_MOTORS);
}

void sendData() {
  if (!hostIP)
    return;

  char buf[128];
  snprintf(buf, sizeof(buf), "%.2f;%.2f;%.2f;%.2f", pressure, temperature,
           depth, altitude);

  udpSend.beginPacket(hostIP, UDP_SEND_PORT);
  udpSend.print(buf);
  udpSend.endPacket();
}

void readSensors() {
  if (bar) {
    bar02.read();
    pressure = bar02.pressure();
    temperature = bar02.temperature();
    depth = bar02.depth();
    altitude = bar02.altitude();
  }
}

/* ===================== SETUP ===================== */
void setup() {
  Serial.begin(115200);

  WT32_ETH01_onEvent();
  ETH.begin(ETH_PHY_ADDR, ETH_PHY_POWER);
  ETH.config(myIP, myGW, mySN, myDNS);
  WT32_ETH01_waitForConnect();

  Serial.print("IP: ");
  Serial.println(ETH.localIP());

  udp.begin(UDP_PORT);
  Serial.print("UDP escuchando en puerto ");
  Serial.println(UDP_PORT);

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);

  pca9685.begin();
  pca9685.setOscillatorFrequency(OSC_FREQ);
  pca9685.setPWMFreq(PWM_FREQ);

  stopAllMotors();
  Serial.println("PCA9685 OK");

  if (bar) {
    if (!bar02.init()) {
      Serial.println("ERROR: Bar02 no encontrado en 0x76");
      while (true)
        ;
    }
    bar02.setModel(MS5837::MS5837_02BA);
    bar02.setFluidDensity(1029); // Agua salada
    Serial.println("Bar02 OK");
  }

  lastPacketTime = millis();
}

/* ===================== LOOP ===================== */
void loop() {
  readSensors();

  int packetSize = udp.parsePacket();

  if (packetSize > 0) {
    hostIP = udp.remoteIP();
    lastPacketTime = millis(); // Guarda el tiempo del último comando recibido

    int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
    if (len > 0)
      packetBuffer[len] = '\0';

    uint16_t pwms[NUM_MOTORS];
    if (parsePacket(packetBuffer, pwms)) {
      setMotors(pwms);
    }
  }

  // Verificación de Watchdog
  if (millis() - lastPacketTime > WATCHDOG_MS) {
    stopAllMotors(); // Apaga/neutraliza motores si pierde conexión
  }

  // Envío de telemetría controlado por tiempo (cada 100 ms)
  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    sendData();
    lastTelemetryTime = millis();
  }
}
