"""
@file       main_lab2_variant4.py
@author     Коровин Данила Юрьевич ВТ-1-24
@version    1.0
@date       01.06.2026
@brief      Практическая работа №2. Отладка обработки отрицательных температур.

@details
  Тема: Отладка программного кода для устройств промышленного интернета вещей.
  Индивидуальное задание №4: неправильная обработка отрицательных температур.
  Инструмент проверки: тест с эмуляцией датчика < 0°C.

Функциональность:
  - эмуляция показаний датчика DHT22;
  - проверка ошибки обработки отрицательных температур;
  - исправление логики обработки температуры;
  - вывод диагностических сообщений в терминал;
  - имитация MQTT-сообщения в формате JSON.

Компетенции: ПК 4.1, ОК 01, ОК 02
"""

import json
import time


DEVICE_ID = "1"
MQTT_TOPIC = "sensors/workshop_1/temperature"

TEMP_ON = 35.0
TEMP_OFF = 28.0

SENSOR_PERIOD = 2
MQTT_PERIOD = 10


def emulate_dht22_values():
    """
    Эмулирует показания датчика.
    В список специально добавлены отрицательные температуры для проверки
    индивидуального задания №4.
    """
    return [
        (24.5, 58.2),
        (-3.4, 61.0),
        (-12.7, 64.5),
        (36.8, 55.1),
        (27.0, 60.3),
    ]


def process_temperature_bug(temperature):
    """
    Ошибочная обработка температуры.

    Проблема: используется abs(temperature), поэтому отрицательная температура
    превращается в положительную. Например, -12.7 становится 12.7.
    Из-за этого в MQTT и диагностике передаются неверные данные.
    """
    normalized_temperature = abs(temperature)
    return normalized_temperature


def process_temperature_fixed(temperature):
    """
    Исправленная обработка температуры.

    Отрицательная температура должна сохранять знак минус, потому что датчик
    может использоваться в холодильных камерах, на улице или в неотапливаемом
    помещении.
    """
    return temperature


def control_ventilation(temperature):
    """
    Управляет вентиляцией по температуре.
    """
    if temperature > TEMP_ON:
        return "HIGH", "Вентиляция включена"

    if temperature < TEMP_OFF:
        return "LOW", "Вентиляция выключена"

    return "NO_CHANGE", "Состояние вентиляции не изменено"


def build_json(temperature, humidity):
    """
    Формирует JSON-сообщение для отправки на MQTT-брокер.
    """
    payload = {
        "device_id": DEVICE_ID,
        "temp": temperature,
        "hum": humidity,
    }

    return json.dumps(payload, ensure_ascii=False)


def debug_negative_temperature_test():
    """
    Выполняет тест индивидуального задания №4.
    Сравнивает ошибочную и исправленную обработку отрицательных температур.
    """
    print("Практическая работа №2")
    print("Автор: Коровин Данила Юрьевич, группа ВТ-1-24")
    print("Индивидуальное задание №4")
    print("Проверка обработки отрицательных температур")
    print("-" * 60)

    for temperature, humidity in emulate_dht22_values():
        print(f"Исходные данные датчика: T = {temperature}°C, H = {humidity}%")

        bug_temperature = process_temperature_bug(temperature)
        fixed_temperature = process_temperature_fixed(temperature)

        print(f"Было с ошибкой: T = {bug_temperature}°C")
        print(f"Стало после исправления: T = {fixed_temperature}°C")

        if temperature < 0 and bug_temperature != temperature:
            print("Обнаружена ошибка: отрицательная температура потеряла знак минус")
            print("Причина: в коде использовалась функция abs(temperature)")
            print("Исправление: передавать temperature без abs()")

        relay_state, relay_message = control_ventilation(fixed_temperature)
        mqtt_payload = build_json(fixed_temperature, humidity)

        print(f"Состояние реле: {relay_state}")
        print(relay_message)
        print(f"MQTT topic: {MQTT_TOPIC}")
        print(f"MQTT payload: {mqtt_payload}")
        print("-" * 60)

        time.sleep(0.5)


def main():
    """
    Главная функция программы.
    """
    debug_negative_temperature_test()


if __name__ == "__main__":
    main()
