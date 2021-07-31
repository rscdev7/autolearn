"""
@author           	:  rscalia
@build-date         :  Sat 31/07/2021
@last_update        :  Sat 31/07/2021

Questo componente serve per lanciare il domain work del microservizio Session che permette di aggiornare un record di Sessione sul DB
"""
from lib.domain_work.worker import guard


guard("session_update_guard")