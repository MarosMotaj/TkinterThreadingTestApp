#!/usr/bin/env python

import RPi.GPIO as GPIO
import adafruit_dht
from time import sleep


class DHT22:

    def __init__(self, dht22_pin, the_queue):

        self.the_queue = the_queue
        GPIO.setmode(GPIO.BCM)
        self.dht22_pin = dht22_pin
        GPIO.setup(self.dht22_pin, GPIO.IN)
        self.dhtDevice = adafruit_dht.DHT22(self.dht22_pin)

    def measure(self, the_event):
        """Metoda cita v nekonecnej loope data z DHT22 senzora
           tieto data posiela cez put() do queue aby boli dostupne
           pre main vlakno GUI rozhrania"""
        while not the_event.is_set():
            try:
                temperature_c = self.dhtDevice.temperature
                # temperature_f = temperature_c * (9 / 5) + 32
                # humidity = self.dhtDevice.humidity

                self.the_queue.put(f"Teplota: {temperature_c} ℃")
                sleep(1)

            # Chyby na DHT22 vznikaju casto z dovodu obtiazneho citania jeho dat,
            # preto aby program pokracoval je nutne zadat vynimku
            except RuntimeError as error:
                print(error.args[0])

            if the_event.is_set():
                break
