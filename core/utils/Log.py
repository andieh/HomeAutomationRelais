import logging
import sys
import os

class Logger:
    singleton = None
    def __init__(self):
        if Logger.singleton:
            self.logger = Logger.singleton.logger
        else:
            self.logger = logging.getLogger("PiHomeAssist")

            # set log level based on config parameter
            level = "debug"
            if not level in ["debug", "info", "warning", "error", "critical"]:
                self.warning("unknown log level {}".format(level))

            self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

            # create formatter
            self.fmt = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
            self.fmt.datefmt = '%m/%d/%Y %H:%M:%S'

            # create console handler and set level to debug
            ch = logging.StreamHandler()

            # add formatter to ch
            ch.setFormatter(self.fmt)

            # add ch to logger
            self.logger.addHandler(ch)

            Logger.singleton = self

            self.log_file = None

    def debug(self, msg):
        self.logger.debug(msg)
    def info(self, msg):
        self.logger.info(msg)
    def warning(self, msg):
        self.logger.warning(msg)
    def error(self, msg):
        self.logger.error(msg)
    def critical(self, msg):
        self.logger.critical(msg)

    def add_handler(self, handler):
        self.logger.addHandler(handler)

    def set_log_destination(self, folder):
        if not os.path.exists(folder):
            self.warning("log output folder {} does not exists, do not log to file!".format(folder))
            return
        if self.log_file:
            log.debug("already write log file to {}".format(self.log_file))
            return self.log_file

        self.log_file = os.path.join(folder, "output.log")

        fh = logging.FileHandler(self.log_file)
        fh.setFormatter(self.fmt)
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        log.debug("start to dump log to {}".format(self.log_file))

        return self.log_file

log = Logger()

