import gzip
import logging
import logging.handlers
import os
import shutil

logging.basicConfig()

class MeticulousLogger:
    _path = "./logs"
    _rh = None
    _f = None
    _sh = None

    LOGLEVEL=os.getenv('LOGLEVEL', 'DEBUG').upper()
    FORCE_STDOUT_LOG=os.getenv("FORCE_STDOUT_LOG", 'False').lower() in ('true', '1', 'y')

    def setLogPath(path):
        MeticulousLogger._path = path
        MeticulousLogger._createHandler();

    def setFileLogLevel(level):
        if MeticulousLogger._rh is None:
            MeticulousLogger._createHandler()
        MeticulousLogger._rh.setLevel(level)

    # Callback when a new log is created
    def cb_logname(name):
        return name + ".gz"

    # function called to rotatethe log at a certain size or time
    def cb_logrotate(source, dest):
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)

    def _createHandler():
        MB = 1024 * 1024
        # Create directory for the logfiles if it doesn't exist
        os.makedirs(MeticulousLogger._path, exist_ok=True)
        logfilePath = os.path.join(MeticulousLogger._path, 'backend.log')
        
        MeticulousLogger._rh = logging.handlers.RotatingFileHandler(
            logfilePath, maxBytes=200*MB, backupCount=10)
        MeticulousLogger._rh.rotator = MeticulousLogger.cb_logrotate
        MeticulousLogger._rh.namer = MeticulousLogger.cb_logname

        MeticulousLogger._f = logging.Formatter(logging.BASIC_FORMAT)
        MeticulousLogger._rh.setFormatter(MeticulousLogger._f)
        MeticulousLogger._rh.doRollover()
        MeticulousLogger._sh = logging.StreamHandler()

    def getLogger(name):
        if MeticulousLogger._rh is None:
            MeticulousLogger._createHandler()

        logger = logging.getLogger(name=name)
        if MeticulousLogger._rh not in logger.handlers:
            logger.addHandler(MeticulousLogger._rh)
        # This will lead to double logging on some systems, so it is disabled by default
        if MeticulousLogger.FORCE_STDOUT_LOG and MeticulousLogger._sh not in logger.handlers:
            logger.addHandler(MeticulousLogger._sh)
        logger.setLevel(MeticulousLogger.LOGLEVEL)
        return logger
