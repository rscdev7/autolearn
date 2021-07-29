"""
@author           	:  rscalia
@build-date         :  Wed 28/07/2021
@last_update        :  Thu 29/07/2021

Questo componente serve per lanciare il domain work del microservizio Storage che permette di archiviare i record sul DB di Storage
"""
from lib.domain_work.worker import guard


guard()