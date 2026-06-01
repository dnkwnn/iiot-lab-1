"""
@file       mqtt_publish_lab2.py
@author     Коровин Данила Юрьевич ВТ-1-24
@version    1.0
@date       01.06.2026
@brief      Публикация MQTT-сообщения для проверки в MQTT Explorer.

Этот файл нужен для рисунка №7 MQTT в практической работе №2.
Код отправляет JSON-сообщение с отрицательной температурой на публичный
MQTT-брокер broker.hivemq.com.
"""

import json
import time

import paho.mqtt.client as mqtt


BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
MQTT_TOPIC = "sensors/workshop_1/temperature"


def main():
    payload = {
        "device_id": "1",
        "student": "Коровин Данила Юрьевич",
        "group": "ВТ-1-24",
        "lab": "Практическая работа №2",
        "variant": 4,
        "temp": -12.7,
        "hum": 64.5,
        "debug_result": "negative temperature fixed",
    }

    message = json.dumps(payload, ensure_ascii=False)

    client = mqtt.Client(client_id="korovin_lab2_variant4")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    print("MQTT broker connected")
    print(f"Topic: {MQTT_TOPIC}")
    print(f"Payload: {message}")

    client.publish(MQTT_TOPIC, message)
    client.loop_start()
    time.sleep(2)
    client.loop_stop()
    client.disconnect()

    print("MQTT message sent")


if __name__ == "__main__":
    main()
