"""
@file       main.py
@author     Коровин Данила Юрьевич ВТ-1-24
@version    1.0
@date       27.05.2026
@brief      Программа управления вентиляцией по данным датчика DHT22 на MicroPython

@details
  Устройство: ESP32 / Arduino
  Датчик: DHT22 (пин 2)
  Реле: пин 9
  Протокол: MQTT
  Брокер: broker.example.com:1883

Функциональность:
  - Опрос датчика каждые 2 секунды
  - Включение вентиляции при T > 35°C
  - Выключение при T < 28°C
  - Отправка MQTT каждые 10 секунд
  - Буферизация при потере связи

Компетенции: ПК 4.1, ОК 01, ОК 02
"""

import json
import random
import time
from collections import deque


DEVICE_ID = "1"
MQTT_TOPIC = "sensors/workshop_1/temperature"

TEMP_ON = 35.0
TEMP_OFF = 28.0

SENSOR_PERIOD = 2
MQTT_PERIOD = 10
BUFFER_SIZE = 100

relay_state = False
data_buffer = deque(maxlen=BUFFER_SIZE)


def read_dht22():
    """
    Имитирует чтение температуры и влажности с датчика DHT22.
    """
    sensor_error = random.random() < 0.05

    if sensor_error:
        return None, None

    temperature = round(random.uniform(24.0, 42.0), 1)
    humidity = round(random.uniform(40.0, 75.0), 1)

    return temperature, humidity


def mqtt_connected():
    """
    Имитирует состояние подключения к MQTT-брокеру.
    """
    return random.random() > 0.2


def control_ventilation(temperature):
    """
    Управляет реле вентиляции по температуре.
    """
    global relay_state

    if temperature > TEMP_ON:
        relay_state = True
        print("Вентиляция включена")

    elif temperature < TEMP_OFF:
        relay_state = False
        print("Вентиляция выключена")


def build_json(temperature, humidity):
    """
    Формирует JSON-сообщение для передачи на MQTT-брокер.
    """
    message = {
        "device_id": DEVICE_ID,
        "temp": temperature,
        "hum": humidity,
    }

    return json.dumps(message, ensure_ascii=False)


def send_mqtt(payload):
    """
    Имитирует отправку сообщения на MQTT-брокер.
    """
    print(f"MQTT отправлено в {MQTT_TOPIC}: {payload}")


def save_to_buffer(payload):
    """
    Сохраняет сообщение в буфер при потере MQTT-связи.
    """
    if len(data_buffer) < BUFFER_SIZE:
        data_buffer.append(payload)
        print("MQTT недоступен, данные сохранены в буфер")
    else:
        print("Буфер переполнен, данные потеряны")


def send_buffered_data():
    """
    Отправляет накопленные сообщения после восстановления связи.
    """
    while data_buffer:
        payload = data_buffer.popleft()
        send_mqtt(payload)


def main():
    """
    Главный цикл программы.
    """
    print("Система запущена")
    print("Автор: Коровин Данила Юрьевич, группа ВТ-1-24")
    print("Wi-Fi подключен")
    print("MQTT подключен")

    last_sensor_read = time.time()
    last_mqtt_send = time.time()

    current_temperature = 0.0
    current_humidity = 0.0

    while True:
        current_time = time.time()

        if current_time - last_sensor_read >= SENSOR_PERIOD:
            temperature, humidity = read_dht22()

            if temperature is None or humidity is None:
                print("Ошибка чтения датчика DHT22")
            else:
                current_temperature = temperature
                current_humidity = humidity

                print(
                    f"Температура: {current_temperature}°C, "
                    f"Влажность: {current_humidity}%"
                )

                control_ventilation(current_temperature)

            last_sensor_read = current_time

        if current_time - last_mqtt_send >= MQTT_PERIOD:
            payload = build_json(current_temperature, current_humidity)

            if mqtt_connected():
                send_mqtt(payload)
                send_buffered_data()
            else:
                save_to_buffer(payload)

            last_mqtt_send = current_time

        time.sleep(0.1)


if __name__ == "__main__":
    main()
