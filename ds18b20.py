#!/usr/bin/env python

import os
from time import sleep


class DS18B20:

    def __init__(self, the_queue):
        self.the_queue = the_queue
        # Nahratie ovladacov
        self.w1_gpio = os.system('modprobe w1-gpio')
        self.w1_therm = os.system('modprobe w1-therm')

        # Definovanie lokality subory s vystupnymi datami zo senzoru
        self.temp_sensor_file = '/sys/bus/w1/devices/28-01192fb12815/w1_slave'

    def read_temp_raw(self):
        """Metoda ktora vracia riadky zo suboru s vystupnymi datami senzora"""
        f = open(self.temp_sensor_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
      """Metoda ktora ziskava data o nameranej teplota zo zdrojoveho suboru"""
      lines = self.read_temp_raw()
      while lines[0].strip()[-3:] != 'YES':
        sleep(0.2)
        lines = self.read_temp_raw()

      temp_result = lines[1].find('t=')

      if temp_result != -1:
        temp_string = lines[1].strip()[temp_result + 2:]
        # Teplota v stupnoch celzia
        self.temp = float(temp_string) / 1000.0
        # Teplota v stupnoch Fahrenheita
        #temp = ((float(temp_string) / 1000.0) * (9.0 / 5.0)) + 32.0

    def measure(self, the_event):
        """Metoda ktora spusta meranie teploty. Do argumentu metody som vlozil (Event())
           aby bolo mozne metodu riadit z ineho vlakna. Metoda posiela do (Queue())
           data v podobe nameranej teploty."""
        while not the_event.is_set():
            self.read_temp()
            self.the_queue.put(f"Teplota: {self.temp} ℃")
            sleep(1)

            if the_event.is_set():
                break

