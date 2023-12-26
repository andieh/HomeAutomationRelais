from threading import Thread
from core.utils.Log import log
import time

class HARBase(Thread):
    def __init__(self, cfg):
        Thread.__init__(self)
        self._inited = False
        self._cfg = cfg
        self._name = self._cfg["name"]
        self._running = True
        self._info = {}
        self._inited = self._init()
        log.debug("inited module '{}'".format(self._name))

    def activate(self):
        pass

    def deactivate(self):
        pass

    def is_active(self):
        pass

    def _check(self):
        pass

    def _init(self):
        return True

    def toggle(self):
        if self.is_active():
            self.deactivate()
        else:
            self.activate()

    def exit(self):
        if self._inited:
            self.deactivate()
            time.sleep(.5)
            self._running = False
            self._update_info("status", "exited")

    def get_info(self):
        base = {\
                "status": "ok" if self._inited else "failed", \
                "running": self.is_running(), \
                "active": self.is_active(), \
            }
        base.update(self._info)
        return base

    def _update_info(self, key, value):
        self._info["key"] = value

    def is_running(self):
        return self._running

    def __del__(self):
        log.debug("exit module '{}'".format(self._name))
        self.exit()

    def run(self):
        if not self._inited:
            log.error("module not initied, do not start main loop")
            return
                
        log.debug("'{}': start checking".format(self._name))
        while self._running:
            self._check()
            time.sleep(0.1)

