from gpiozero import MotionSensor
from core.utils.Log import log
from core.Pi.HARBase import HARBase
import time
from datetime import datetime,timedelta
import os

class HARPir(HARBase):
    __category__ = "led"
    def _init(self):
        if not "port" in self._cfg:
            log.error("port not specified, aborting")
            return False
        port = self._cfg["port"]
        self._min_on = self._cfg["min_on"] if "min_on" in self._cfg else 30
        self._pir = MotionSensor(port)
        self._pir.when_motion = self.activate
        self._last_motion = datetime.utcnow()
        self._on = False
        return True
        
    def activate(self):
        now = datetime.utcnow()
        log.debug("motion detected, reset timer")
        self._last_motion = now

    def execute(self, cmd):
        log.debug("execute command '{}'".format(cmd))
        os.system(cmd)

    def deactivate(self):
        pass

    def is_active(self):
        return self._on

    def _check(self):
        now = datetime.utcnow()
        on_time = now - self._last_motion
        action_time = on_time < timedelta(seconds=self._min_on)
        off_cmd = "xset -display :0.0 dpms force off"
        on_cmd = "xset -display :0.0 dpms force on"

        if not self._on and action_time:
            self.execute(on_cmd)
            self._on = True
        elif self._on and not action_time:
            self.execute(off_cmd)
            self._on = False


