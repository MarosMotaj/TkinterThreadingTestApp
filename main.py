#!/usr/bin/env python

"""
Dovod vytvorenia tejto aplikacie bol ten, ze som sa chcel naucit pracovat s vlaknami v Pythone.
Vyvijana bola na Raspberry Pi4 4BG, ktore ponuka moznost prace s realnymi datami zo senzorov,
teda moznost ucenia sa pracovat s vlaknami na realnych datach.
"""

from threading import Thread, Event
from queue import Queue
import time
from dht22 import DHT22
from ds18b20 import DS18B20
from leds import Leds
import tkinter as tk
import RPi.GPIO as GPIO


class App(tk.Tk):

    def __init__(self):

        super().__init__()
        self.dht22_queue = Queue()
        self.dht22_event = Event()

        self.ds18b20_queue = Queue()
        self.ds18b20_event = Event()

        # Do konstruktorov objektov senzorov som vlozil instanciu na Queue(), ktore nam umozni
        # zdielat data medzi vlaknami
        self.dht22 = DHT22(22, self.dht22_queue)
        self.ds18b20 = DS18B20(self.ds18b20_queue)

        self.dht22_leds = Leds(5, 6)
        self.dht22_leds.red_led_on()
        self.dht22_leds.green_led_off()
        self.ds18b20_leds = Leds(23, 24)
        self.ds18b20_leds.red_led_on()
        self.ds18b20_leds.green_led_off()

        self.title("Sensor App")
        self.geometry("+450+300")
        self.geometry("345x150")

        self.dht22_output_data = tk.StringVar()
        self.dht22_output_data.set("Sensor is off")

        self.ds18b20_output_data = tk.StringVar()
        self.ds18b20_output_data.set("Sensor is off")

        self.dht22_data_view = tk.Label(self, textvariable=self.dht22_output_data, height=2, width=15, borderwidth=3, relief="sunken")
        self.dht22_data_view.grid(row=0, column=1, padx=5, sticky=tk.EW)

        self.ds18b20_data_view = tk.Label(self, textvariable=self.ds18b20_output_data, height=2, width=15, borderwidth=3, relief="sunken")
        self.ds18b20_data_view.grid(row=0, column=0, padx=5, sticky=tk.EW)

        self.button_start_dht22 = tk.Button(self, text="Start DHT22", height=2, width=15, bg="silver", fg="blue")
        self.button_start_dht22['command'] = lambda: self.start_dht22_sensor()
        self.button_start_dht22.grid(row=1, column=1, padx=5, sticky=tk.EW)

        self.button_stop_dht22 = tk.Button(self, text="Stop DHT22", height=2, width=15, bg="silver", fg="red")
        self.button_stop_dht22['command'] = lambda: self.stop_dht22_sensor()
        self.button_stop_dht22.grid(row=2, column=1, padx=5, sticky=tk.EW)

        self.button_start_ds18b20 = tk.Button(self, text="Start DS18B20", height=2, width=15, bg="silver", fg="blue")
        self.button_start_ds18b20['command'] = lambda: self.start_ds18b20_sensor()
        self.button_start_ds18b20.grid(row=1, column=0, padx=5, sticky=tk.EW)

        self.button_stop_ds18b20 = tk.Button(self, text="Stop DS18B20", height=2, width=15, bg="silver", fg="red")
        self.button_stop_ds18b20['command'] = lambda: self.stop_ds18b20_sensor()
        self.button_stop_ds18b20.grid(row=2, column=0, padx=5, sticky=tk.EW)

        # self.button_check_alive_threads = tk.Button(self, text="alive_threads")
        # self.button_check_alive_threads['command'] = lambda: self.alive_threads()
        # self.button_check_alive_threads.grid(row=5, column=0, padx=5, sticky=tk.EW)

    def start_dht22_sensor(self):
        """Tato metoda vytvori vlakno v ktorom bezi funkcia merania z objektu DHT22
           Do argumentu funkcie merania som vlozil (Event()) ktore nam umozni
           spustat a zastavit danu metodu z ineho vlakna. Po spusteni sa
           rozsvieti zelena LED a zhasne cervena LED"""

        self.dht22_thread = Thread(target=self.dht22.measure, args=(self.dht22_event, ))
        # Musi byt daemon True, inak sa po zatvoreni app a pri beziacom DHT22 vlakne, program neukonci!
        self.dht22_thread.daemon = True
        self.after(1000, self.refresh_dht22_data)
        self.dht22_thread.start()
        self.dht22_leds.green_led_on()
        self.dht22_leds.red_led_off()

    def refresh_dht22_data(self):
        """Metoda sluzi na obnovu zobrazovanych dat zo senzora DHT22 v GUI"""

        if not self.dht22_thread.is_alive() and not self.dht22_queue.empty():
            return

        # obnov GUI novymi datami z queue
        while not self.dht22_queue.empty():
            # print(self.dht22_queue.get())
            self.dht22_output_data.set(self.dht22_queue.get())

        # casovac pre obnovu dat
        self.after(1000, self.refresh_dht22_data)

    def stop_dht22_sensor(self):
        """Metoda najpv set() funkciou zastavi While loop vo vlakne dht22_thread
           nasledne pocka 2 sekundy kym sa neukonci proces beziaci v danej While loop
           v dalsich krokoch aby bolo mozne opatovne spustat DHT22 senzor je nutne:
           - vyprazdnit data v Queue
           - vyresetovat Event set()
           - ukoncit vlakno dht22_thread"""

        self.dht22_event.set()
        time.sleep(2)
        self.dht22_queue.empty()
        self.dht22_event.clear()
        self.dht22_thread.join()
        self.dht22_output_data.set("Sensor is off")
        self.dht22_leds.green_led_off()
        self.dht22_leds.red_led_on()

    def start_ds18b20_sensor(self):
        """Tato metoda vytvori vlakno v ktorom bezi funkcia merania z objektu DS18B20
           Do argumentu funkcie merania som vlozil (Event()) ktore nam umozni
           spustat a zastavit danu metodu z ineho vlakna. Po spusteni sa
           rozsvieti zelena LED a zhasne cervena LED"""

        self.ds18b20_thread = Thread(target=self.ds18b20.measure, args=(self.ds18b20_event, ))
        # Musi byt daemon True, inak sa po zatvoreni app a pri beziacom DS18B20 vlakne, program neukonci!
        self.ds18b20_thread.daemon = True
        self.after(1000, self.refresh_ds18b20_data)
        self.ds18b20_thread.start()
        self.ds18b20_leds.green_led_on()
        self.ds18b20_leds.red_led_off()

    def refresh_ds18b20_data(self):
        """Metoda sluzi na obnovu zobrazovanych dat zo senzora DS18B20 v GUI"""

        if not self.ds18b20_thread.is_alive() and not self.ds18b20_queue.empty():
            return

        # obnov GUI novymi datami z queue
        while not self.ds18b20_queue.empty():
            # print(self.ds18b20_queue.get())
            self.ds18b20_output_data.set(self.ds18b20_queue.get())

        # casovac pre obnovu dat
        self.after(1000, self.refresh_ds18b20_data)

    def stop_ds18b20_sensor(self):
        """Metoda najpv set() funkciou zastavi While loop vo vlakne ds18b20_thread
           nasledne pocka 2 sekundy kym sa neukonci proces beziaci v danej While loop
           v dalsich krokoch aby bolo mozne opatovne spustat DS18B20 senzor je nutne:
           - vyprazdnit data v Queue
           - vyresetovat Event set()
           - ukoncit vlakno ds18b20_thread"""

        self.ds18b20_event.set()
        time.sleep(2)
        self.ds18b20_queue.empty()
        self.ds18b20_event.clear()
        self.ds18b20_thread.join()
        self.ds18b20_output_data.set("Sensor is off")
        self.ds18b20_leds.green_led_off()
        self.ds18b20_leds.red_led_on()

    # def alive_threads(self):
    #     """Tato metoda vypise aktualne beziace vlakna
    #        Urcena na testovanie pri vyvoji tejto app"""
    #     for thread in threading.enumerate():
    #         print(thread.getName())


if __name__ == '__main__':
    app = App()
    app.mainloop()
    GPIO.cleanup()

