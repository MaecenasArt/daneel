import logging
import logging.handlers

def setLogger(logFilename, logLevel):
    formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.handlers.TimedRotatingFileHandler(logFilename, when="midnight", backupCount=14)
    handler.setFormatter(formatter)
    log = logging.getLogger()
    log.setLevel(logLevel)
    log.addHandler(handler)
    return log