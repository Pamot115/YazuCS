# -*- coding: utf-8 -*-

import sys
import os
import logging


logger = logging.getLogger()

"""
Se detienen todos los threads en ejecución
"""

def exit_cleanup():
    if 'camera' in vars():
        camera.stop_recording()
        camera.close()

def exit_clean(signal=None, frame=None):
    logger.info("Yazu stopping...")
    exit_cleanup()
    sys.exit(0)

def exit_error(message):
    logger.critical(message)
    exit_cleanup()
    sys.exit(1)

def exception_handler(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(repr(value)))
