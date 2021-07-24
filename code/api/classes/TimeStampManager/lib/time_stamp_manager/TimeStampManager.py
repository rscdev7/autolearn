"""
@author           	:  rscalia
@build-date         :  Sun 02/05/2021
@last_update        :  Fri 23/07/2021

Questo componente serve per convertire una data in un Timestamp UNIX e viceversa oltre che a restituire il timestamp attuale in millisecondi.
"""

from datetime 		import datetime 
import time
from typing 		import Union


class TimeStampManager:

	@staticmethod
	def date2Timestamp (pDay:int, pMonth:int , pYear:int , pHour=0 , pMinutes=0) -> Union [ int , Exception]:
		"""
		Converte una data in un timestamp UNIX (in secondi).

		Args:\n
			pDay 		(int)				: giorno
			pMonth 		(int)				: mese
			pYear 		(int)				: anno
			pHour 		(int | DEF = 0)		: ora
			pMinutes 	(int | DEF = 0)		: minuti

		Returns:\n
			Union [ int , Exception ]		: timestamp UNIX in Secondi o eccezione

		Raises:\n
			Exception						: eccezione molto probabilmente scaturità da un formato dei parametri passati inammissibile.
		"""
		try:
			dt:datetime				= datetime (day=pDay, month=pMonth, year=pYear, hour=pHour, minute=pMinutes)
			timestamp:float		    = dt.timestamp()
			return int(timestamp)

		except Exception as msg:
			return msg


	@staticmethod
	def timestamp2Date (pTimeStamp:int , pStringOut=True) -> Union[ str , datetime]:
		"""
		Converte un timestamp UNIX (in secondi) in una Data.

		Args:\n
			pTimeStamp 		(int)					: numero in virgola mobile rappresentante un timestamp in secondi
			pStringOut		(bool | DEF = True) 	: Se impostato a vero, il metodo restituisce una data formattata come stringa, atrimenti restituisce la data incapsulata in un oggetto datetime.

		Returns:\n
			Union[ str , datetime]					: stringa o oggetto datetime rappresentante la data associata al timestamp passato alla funzione
		"""
		dt:datetime			= datetime.fromtimestamp(pTimeStamp)

		if (pStringOut == True):
			strDate:str     = dt.strftime("%d-%m-%Y %H:%M")
			return strDate
		else:
			return dt	


	@staticmethod
	def currentTimeStampInMS () -> int:
		"""
		Restituisce il timestamp Attuale in millisecondi.

		Returns:\n
			int					: timestamp in millisecondi
		"""
		return round(time.time() * 1000)

	
	@staticmethod
	def currentTimeStampInSec () -> int:
		"""
		Restituisce il timestamp Attuale in millisecondi.

		Returns:\n
			int					: timestamp in secondi
		"""
		return int( time.time() )