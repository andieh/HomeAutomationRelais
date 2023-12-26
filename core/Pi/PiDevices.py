from threading import Thread
import time
from datetime import datetime, timedelta
from core.Pi.HARLed import HARLed
from core.Pi.HARPwmLed import HARPwmLed
from core.utils.Log import log

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
            obj = HARPwmLed(definition)
        elif category == "LED":
            if not "port" in definition:
                log.error("no port configured for {}".format(name))
                return False
            obj = HARLed(definition)
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

