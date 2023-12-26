from gpiozero import LED
from core.utils.Log import log
from core.Pi.HARBase import HARBase
import time

class HARLed(HARBase):
    __category__ = "led"
    def _init(self):
        if not "port" in self._cfg:
            log.error("port not specified, aborting")
            return False
        port = self._cfg["port"]
        active_high = self._cfg["active_high"] if "active_high" in self._cfg else True
        initial_value = self._cfg["initial"] if "initial" in self._cfg else False
        log.debug("inited new LED on port {}, active high: {}, initial value: {}"\
                .format(port, active_high, initial_value))
        self._device = LED(port, active_high=active_high, initial_value=initial_value)
        self._request_on = None
        self._request_off = None
        self._on = initial_value
        return True
        
    def activate(self):
        log.debug("Turn on LED")
        self._request_on = True

    def deactivate(self):
        log.debug("Turn off LED")
        self._request_off = True

    def is_active(self):
        return self._on

    def _check(self):
        if self._request_on:
            self._device.on()
            log.debug("Turn on Device")
            self._on = True
            self._request_on = None
        
        if self._request_off:
            self._device.off()
            log.debug("Turn off Device")
            self._request_off = None
            self._on = False



