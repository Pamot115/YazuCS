# -*- coding: utf-8 -*-

import logging
import time


logger = logging.getLogger()


def process_photos(rpis, camera):
    """
    Crea una cola con fotos a procesar y verifica que el dispositivo de "control" no esté en la red antes de enviar las 
    fotos por Telegram, además, remueve las fotos de la cola una vez que se envían
    """
    logger.info("thread running")
    while True:
        if not camera.queue.empty():
            if rpis.state.current == 'Escaneando':
                logger.debug('Running arp_ping_macs before sending photos...')
                rpis.arp_ping_macs()
                time.sleep(5)
                while not camera.queue.empty():
                    if rpis.state.current != 'Escaneando':
                        logger.debug('Stopping photo processing as state is now {0} and clearing queue'.format(rpis.state.current))
                        camera.clear_queue()
                        break
                    photo = camera.queue.get()
                    logger.debug('Processing the photo {0}, state is {1}'.format(photo, rpis.state.current))
                    rpis.state.update_triggered(True)
                    rpis.telegram_send_message('Movimiento detectado')
                    if rpis.telegram_send_file(photo):
                        camera.queue.task_done()
            else:
                logger.debug('Stopping photo processing as state is now {0} and clearing queue'.format(rpis.state.current))
                camera.clear_queue()
        time.sleep(0.1)
