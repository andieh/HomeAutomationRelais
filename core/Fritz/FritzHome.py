from threading import Thread
import time
from datetime import datetime, timedelta

from pyfritzhome import *

from core.utils.Log import log

class FritzHome(Thread):
    def __init__(self, host, user, password):
        log.debug("FritzHome start to check")
        Thread.__init__(self)
        
        self._host = host
        self._user = user
        self._pass = password
        self._away = None
        self._check_interval_s = 1 
        self._check_devices_every_s = 10
        self._login_timeout_s = 5
        self._last_checked = datetime.utcnow()-timedelta(seconds=self._check_devices_every_s+1)
        self._running = True
        self._connected = False

        self.devices = {}

        # home automation object
        self.fha = None

    def _connect(self):
        if self.fha:
            log.warning("already object created...")
            return 
        
        self.fha = Fritzhome(self._host, self._user, self._pass)
        try:
            self.fha.login()
        except Exception as e:
            log.error("failed to connect to Fritz Server")
            log.error("error was: {}".format(str(e)))
            self.fha = None
            return 

        print(dir(self.fha))
        self._connected = True

    def stop(self):
        log.debug("stopping to check for FritzHome Devices")
        self._running = False

    def get_away_mode(self):
        return self._away

    def run(self):
        while self._running:
            if not self._connected:
                self._connect()

            if not self._connected:
                log.warning("failed to connect, retry")
                time.sleep(self._login_timeout_s)
                self._login_timeout_s *= 2
                self._login_timeout_s = min(60, self._login_timeout_s)
                continue

            now = datetime.utcnow()
            if (now-self._last_checked).total_seconds() < self._check_devices_every_s:
                time.sleep(self._check_interval_s)
                continue

            try:
                self.fetch_data()
            except Exception as e:
                log.error("failed to fetch data!")
                log.error("error was: {}".format(str(e)))
                print(type(e))
                # requests.exceptions.ConnectTimeout
                time.sleep(self._check_interval_s)
            

    def get_devices(self):
        return self.devices

    def set_switch(self, name, state):
        dev = self.get_device(name)
        if state:       
            self.fha.set_state_on(dev["ain"])
        else:
            self.fha.set_state_off(dev["ain"])
        self.fetch_data()

    def set_temp(self, name, temp):
        dev = self.get_device(name)
        self.fha.set_target_temperature(dev["ain"], temp)
        self.fetch_data()

    def toggle_away_mode(self, temp):
        if self._away:
            log.info("disable away mode")
            self._away = None
            return True

        log.info("enable away mode")
        self._away = temp
        return True

    def get_device(self, name):
        if name in self.devices:
            return self.devices[name]

        log.warning("requested device with name '{}' not found".format(name))
        return {}

    def get_ain_by_name(self, name):
        if not name in self.devices:
            return None
        return self.devices[name]["ain"]

    def update_devices(self):
        self.fha.update_devices()

    def fetch_data(self):
        supported_devices = ["Comet DECT", "FRITZ!DECT 200"]
        log.debug("get data from devices")
        start = time.time()
        self.update_devices()
        for ain, dev in self.fha.get_devices_as_dict().items():
            # get name
            name = dev.name
            # type of the device
            product = dev.productname
            if not product in supported_devices:
                log.debug("skipping (currently) unsupported device {}".format(product))
                continue

            # create new object in our internal database
            if not name in self.devices:
                self.devices[name] = {"status": "unknown", "msg": ""}

            self.devices[name]["ain"] = ain
            self.devices[name]["category"] = product
            self.devices[name]["away"] = self._away if self._away else "no"

            if not dev.present:
                self.devices[name]["status"] = "unavailable"
                self.devices[name]["msg"] = "device not reachable"
                continue

            self.devices[name]["status"] = "ok"
            hts = dev.has_temperature_sensor
            self.devices[name]["has_temp_sensor"] = hts
            if hts:
                self.devices[name]["temperature"] = dev.temperature
            
            hs = dev.has_switch
            self.devices[name]["has_switch"] = hs
            if hs:
                self.devices[name]["state"] = dev.switch_state
            
            hpm = dev.has_powermeter
            self.devices[name]["has_powermeter"] = hpm
            if hpm: 
                self.devices[name]["power"] = dev.power

            htt = dev.has_thermostat
            self.devices[name]["has_thermostat"] = htt
            if htt:
                #stats = self.fha.get_device_statistics(ain)
                self.devices[name]["target"] = dev.target_temperature
                self.devices[name]["eco"] = dev.eco_temperature
                self.devices[name]["comfort"] = dev.comfort_temperature
                self.devices[name]["battery"] = dev.battery_level
                self.devices[name]["window_open"] = dev.window_open
        
        fetch_time = time.time() - start
        log.debug("fetched device infos in {:0.2f}s".format(fetch_time))
        if fetch_time > self._check_devices_every_s:
            new_check = max(10, (int(fetch_time / 10)+1) * 10)
            log.warning("Fetching Device info tooks longer than check interval. increase to {}s".format(new_check))
            self._check_devices_every_s = new_check
        self._last_checked = datetime.utcnow()
