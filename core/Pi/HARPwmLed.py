from gpiozero import PWMLED
from threading import Thread
from core.utils.Log import log
from core.Pi.HARBase import HARBase
import time

class HARPwmLed(HARBase):
    __name__ = "pwmled"
    def _init(self):
        self._device = None
        if not "port" in self._cfg:
            log.error("no port specified")
            return False
        self._port = self._cfg["port"]
        self._on = False
        self._request_on = None
        self._request_off = None
        return True

    def activate(self):
        log.debug("Pulse LED")
        self._request_on = True

    def deactivate(self):
        log.debug("Unpulse LED")
        self._request_off = True

    def is_active(self):
        return self._on

    def _check(self):
        if self._request_on:
            log.debug("init device and start pulsing")
            self._device = PWMLED(self._port)
            self._device.pulse()
            self._request_on = None
            self._on = True

        if self._request_off:
            log.debug("deinit device")
            self._device.close()
            self._device = None
            self._on = False
            self._request_off = None

