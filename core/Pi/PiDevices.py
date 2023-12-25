from threading import Thread
import time
from datetime import datetime, timedelta

from core.utils.Log import log

from gpiozero import PWMLED
class HARPwmLed(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self._port = port
        self._led = None
        self._on = False
        self._pulsing = False
        self._running = True

    def on(self):
        self._on = True

    def off(self):
        self._on = False

    def toggle(self):
        self._on = not self._on

    def exit(self):
        self._running = False

    def get_state(self):
        return self._on

    def get_info(self):
        return {
            "pulsing": self._pulsing
            }
    def is_running(self):
        return self._running

    def run(self):
        log.debug("HARPwmLed: start checking")
        while self._running:
            if self._on and not self._pulsing:
                log.debug("start pulsing")
                if self._led is None:
                    self._led = PWMLED(self._port)
                self._led.pulse()
                self._pulsing = True

            elif not self._on and self._pulsing:
                log.debug("stop pulsing")
                self._led.close()
                self._led = None
                self._pulsing = False

            time.sleep(0.1)

from gpiozero import LED
class HARLed(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self._port = port
        self._led = None
        self._on = False
        self._request = False
        self._running = True
        self._device = LED(port, active_high=False, initial_value=None)

    def on(self):
        self._on = True
        self._request = True

    def off(self):
        self._on = False
        self._request = True

    def toggle(self):
        if self.get_state():
            self.off()
        else:
            self.on()

    def exit(self):
        self._running = False

    def get_state(self):
        return self._on

    def get_info(self):
        return {
            "state": self._on
            }
    def is_running(self):
        return self._running

    def run(self):
        log.debug("HARPwmLed: start checking")
        while self._running:
            if self._request and self._on:
                log.debug("enable LED")
                self._device.on()

            elif self._request and not self._on:
                log.debug("disable LED")
                self._device.off()
            
            self._request = False
            time.sleep(0.1)

class PiDevices(Thread):
    def __init__(self):
        log.debug("Start to check Pi connected Devices")
        Thread.__init__(self)

        self._gadgets = {}
        self._check_interval_s = 1 
        self._running = True

    def add_gadget(self, definition):
        name = definition["name"] if "name" in definition else None
        if name is None:
            log.error("no name specified for gadget")
            return False

        if name in self._gadgets:
            log.warning("there is already a gadget with name '{}'".format(name))
            return False
        category = definition["category"] if "category" in definition else None
        if category is None:
            log.error("no category specified for gadget with name '{}'".format(name))
            return False

        obj = None
        if category == "PWMLED":
            if not "port" in definition:
                log.error("no port configured for {}".format(name))
                return False
            obj = HARPwmLed(definition["port"])
        elif category == "LED":
            if not "port" in definition:
                log.error("no port configured for {}".format(name))
                return False
            obj = HARLed(definition["port"])
        else:
            log.error("unknown category '{}' for gadget with name '{}'".format(category, name))
            return False

        # start main thread for this gadget
        obj.start()
        self._gadgets[name] = {"obj": obj, "cfg": definition}
        log.debug("added gadget '{}' of type '{}".format(name, category))
    
    def get_state(self, name):
        if not name in self._gadgets:
            log.error("no gadget with name '{}'".format(name))
            return None
        return self._gadgets[name]["obj"].get_state()

    def get_gadgets(self):
        return list(self._gadgets.keys())

    def do_action(self, name):
        gadget = self._gadgets[name]
        gadget["obj"].toggle()
        return True

    def get_gadget(self, name):
        if not name in self._gadgets:
            log.warning("unknown gadget '{}'".format(name))
            return None
        gadget = self._gadgets[name]

        ret = gadget["cfg"]
        obj = gadget["obj"]
        ret.update(obj.get_info())
        status = "ok"
        msg = ""
        if not obj.is_running():
            status = "failed"
            msg = "gadget not running"

        ret["status"] = status
        ret["msg"] = msg
        return ret
    
    def stop(self):
        log.debug("stopping to check for Pi Devices")
        self._running = False

    def run(self):
        while self._running:
            time.sleep(self._check_interval_s)

