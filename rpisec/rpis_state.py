# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from threading import Lock
import time


logger = logging.getLogger()


class RpisState(object):
    '''
    Información de estado, manejo de actualizaciones y alarmas
    '''
    def __init__(self, rpis):
        self.rpis = rpis
        self.lock = Lock()
        self.start_time = time.time()
        self.current = 'Detenido'
        self.previous = 'Sin ejecutarse'
        self.last_change = time.time()
        self.last_packet = time.time()
        self.last_mac = None
        self.triggered = False

    # Estado del sistema
    def update_state(self, new_state):
        assert new_state in ['Escaneando', 'Detenido', 'Deshabilitado']
        if new_state != self.current:
            with self.lock:
                self.previous = self.current
                self.current = new_state
                self.last_change = time.time()
                self.rpis.telegram_send_message("Yazu se encuentra: {0}".format(self.current))
                logger.info("Yazu is now {0}".format(self.current))

    # Regisro de alarmas
    def update_triggered(self, triggered):
        with self.lock:
            self.triggered = triggered
    
    # Última MAC
    def update_last_mac(self, mac):
        with self.lock:
            self.last_mac = mac
            self.last_packet = time.time()

    # Conteo de tiempo
    def _get_readable_delta(self, then):
        td = timedelta(seconds=time.time() - then)
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
        text = '{0} minutos'.format(minutes)
        if hours > 0:
            text = '{0} horas y '.format(hours) + text
            if days > 0:
                text = '{0} días, '.format(days) + text
        return text

    #Escaneo de ARP en base al estado
    def check(self):
        if self.current == 'Deshabilitado':
            return
        now = time.time()
        if now - self.last_packet > (self.rpis.packet_timeout + 20):
            if self.current != 'Escaneando':
                logger.debug("No packets detected for {0} seconds, arming".format(self.rpis.packet_timeout + 20))
            self.update_state('Escaneando')
        elif now - self.last_packet > self.rpis.packet_timeout:
            logger.debug("Running arp_ping_macs before arming...")
            self.rpis.arp_ping_macs()
        else:
            self.update_state('Detenido')

    #Texto para mensaje de estado
    def generate_status_text(self):
        return (
            "*Informe de ejecución*\n"
            "Estado actual: _{0}_ \n"
            "Último estado: _{1}_ \n"
            "Último cambio hace: _{2}_ \n"
            "Tiempo de ejecución: _{3}_ \n"
            "Última MAC detectada: _{4}  hace {5}_ \n"
            "Alarma activada: _{6}_ \n"
            ).format(
                    self.current,
                    self.previous,
                    self._get_readable_delta(self.last_change),
                    self._get_readable_delta(self.start_time),
                    self.last_mac,
                    self._get_readable_delta(self.last_packet),
                    self.triggered
                )
