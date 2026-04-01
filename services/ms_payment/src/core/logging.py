import logging

LOG_LEVEL = "INFO"
LOG_FORMAT_DEBUG = "%(levelname)s:          %(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
LOG_FORMAT_DEFAULT = "%(levelname)s:          %(message)s"


def configure_logging():
    log_format = LOG_FORMAT_DEBUG if LOG_LEVEL == "DEBUG" else LOG_FORMAT_DEFAULT

    logging.basicConfig(level=LOG_LEVEL, format=log_format, force=True)
