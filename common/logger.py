import sys

from .settings import LogConfig

import logging

def _get_log_level(level_conf):
    if level_conf == 'info':
        return logging.INFO
    if level_conf == 'debug':
        return logging.DEBUG
    if level_conf == 'warn':
        return logging.WARNING
    if level_conf == 'error':
        return logging.ERROR
    if level_conf == 'critical':
        return logging.CRITICAL

    return loggin.NOTSET

_level = _get_log_level(LogConfig.LEVEL)

logging.basicConfig(
    datefmt=LogConfig.DATE_FORMAT,
    level=_level,
    format=LogConfig.FORMAT,
)

def get_logger(name):
    logger = logging.getLogger(name)
    return logger

