from threading import Thread
import time
from datetime import datetime, timedelta
import gpiozero

from core.utils.Log import log

class PiDevices(Thread):
    def __init__(self):
        log.debug("Start to check Pi connected Devices")
        Thread.__init__(self)
        self._check_interval_s = 1 
        self._running = True

    def stop(self):
        log.debug("stopping to check for Pi Devices")
        self._running = False

    def run(self):
        while self._running:
            time.sleep(self._check_interval_s)

