/**
 * @file        iiot_temperature_controller.ino
 * @author      __________________
 * @version     1.0
 * @date        27.05.2026
 * @brief       Program for ventilation control by DHT22 sensor data.
 */

#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define DHT_PIN 2
#define DHT_TYPE DHT22
#define RELAY_PIN 9

#define WIFI_SSID "your_SSID"
#define WIFI_PASSWORD "your_PASSWORD"
#define MQTT_SERVER "broker.example.com"
#define MQTT_PORT 1883
#define MQTT_TOPIC "sensors/workshop_1/temperature"

const float TEMP_ON = 35.0;
const float TEMP_OFF = 28.0;
const unsigned long SENSOR_PERIOD = 2000;
const unsigned long MQTT_PERIOD = 10000;

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient mqttClient(espClient);

float currentTemp = 0.0;
float currentHum = 0.0;
bool relayState = false;
unsigned long lastSensorRead = 0;
unsigned long lastMqttSend = 0;

struct DataBuffer {
  char messages[100][128];
  int head = 0;
  int tail = 0;
  int count = 0;

  bool push(const char* msg) {
    if (count >= 100) {
      return false;
    }
    strncpy(messages[head], msg, sizeof(messages[head]) - 1);
    messages[head][sizeof(messages[head]) - 1] = '\0';
    head = (head + 1) % 100;
    count++;
    return true;
  }

  bool pop(char* out) {
    if (count == 0) {
      return false;
    }
    strcpy(out, messages[tail]);
    tail = (tail + 1) % 100;
    count--;
    return true;
  }
};

DataBuffer buffer;

void setupWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Wi-Fi connected");
}

void setupMQTT() {
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  while (!mqttClient.connected()) {
    mqttClient.connect("iiot_temperature_controller");
    delay(500);
  }
  Serial.println("MQTT connected");
}

void controlVentilation(float temp) {
  if (temp > TEMP_ON) {
    relayState = true;
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println("Ventilation ON");
  } else if (temp < TEMP_OFF) {
    relayState = false;
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("Ventilation OFF");
  }
}

String buildJson(float temp, float hum) {
  String json = "{\"device_id\":\"1\",\"temp\":";
  json += String(temp, 1);
  json += ",\"hum\":";
  json += String(hum, 1);
  json += "}";
  return json;
}

void sendMQTT(const char* payload) {
  if (mqttClient.publish(MQTT_TOPIC, payload)) {
    Serial.print("MQTT sent: ");
    Serial.println(payload);
  } else {
    Serial.println("MQTT send failed");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  dht.begin();
  setupWiFi();
  setupMQTT();
  lastSensorRead = millis();
  lastMqttSend = millis();
}

void loop() {
  unsigned long now = millis();

  if (now - lastSensorRead >= SENSOR_PERIOD) {
    currentTemp = dht.readTemperature();
    currentHum = dht.readHumidity();

    if (isnan(currentTemp) || isnan(currentHum)) {
      Serial.println("DHT22 read error");
    } else {
      controlVentilation(currentTemp);
    }

    lastSensorRead = now;
  }

  if (now - lastMqttSend >= MQTT_PERIOD) {
    String json = buildJson(currentTemp, currentHum);

    if (mqttClient.connected()) {
      sendMQTT(json.c_str());

      char bufferedMessage[128];
      while (buffer.pop(bufferedMessage)) {
        sendMQTT(bufferedMessage);
      }
    } else {
      if (buffer.push(json.c_str())) {
        Serial.println("MQTT disconnected, data buffered");
      } else {
        Serial.println("Buffer overflow, data lost");
      }
    }

    lastMqttSend = now;
  }

  if (!mqttClient.connected()) {
    setupMQTT();
  }

  mqttClient.loop();
  delay(100);
}
