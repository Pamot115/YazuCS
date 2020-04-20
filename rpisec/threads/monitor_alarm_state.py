# -*- coding: utf-8 -*-

import logging
import time

logger = logging.getLogger()


def monitor_alarm_state(rpis, camera):
	"""
	Controla el monitoreo e inicia/detiene la  detección de movimiento en basestring
    al estado del bot
	"""
	logger.info("Monitoring thread running")
	time.sleep(2.0)
	while True:
		time.sleep(0.1)
		rpis.state.check()
		if rpis.state.current == 'Escaneando':
			camera.start_motion_detection(rpis)
		else:
			camera.stop_motion_detection()
