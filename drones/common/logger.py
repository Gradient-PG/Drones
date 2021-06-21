import logging


def setup_logger(name: str, log_file: str, level: int = logging.DEBUG) -> logging.Logger:
    """Setup for each logger
    Parameters:
        ----------
            name: str
                Name of log. Every log should have unique name.
            log_file: str
                Path to file to log by this log. Every log should have unique file.
            level: int
                Specify level of logger. Please use levels from logging library.

        Returns:
        ----------
            log: logging.Logger
                Log object will show logs only in file from parameter.
    """
    logging.basicConfig(level=logging.ERROR, handlers=[])
    formatter = logging.Formatter("[%(filename)s] [%(levelname)s] [%(asctime)s]: %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.handlers.clear()
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
