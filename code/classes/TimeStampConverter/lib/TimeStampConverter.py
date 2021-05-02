"""
@author           	:  rscalia
@version  		    :  1.0.1
@build-date         :  Sun 02/05/2021
@last_update        :  Sun 02/05/2021

Questo componente serve per convertire una data in un Timestamp UNIX e viceversa.

"""

from datetime import datetime 


class TimeStampConverter:

	
	def date2Timestamp (self, pDay:int, pMonth:int , pYear:int ,pHour=0 , pMinutes=0) -> float:
		"""
		Converte un timestamp UNIX in una Data.

		Args:
			pDay 		(int)	: giorno
			pMonth 		(int)	: mese
			pYear 		(int)	: anno
			pHour 		(int | default=0)	: ora
			pMinutes 	(int | default=0)	: minuti

		Returns:
			float				: timestamp UNIX
		"""
		try:
			dt:datetime				= datetime (day=pDay, month=pMonth, year=pYear, hour=pHour, minute=pMinutes)
			timestamp:float		    = dt.timestamp()
			return timestamp

		except Exception as msg:
			print ("[!] Exception Occurred, msg => {} ".format(msg))

	
	def timestamp2Date (self, pTimeStamp:float , pStringOut=True) -> (str or datetime):
		"""
		Converte un timestamp UNIX in una Data.

		Args:
			pTimeStamp 		(float)	: numero in virgola mobile rappresentante un timestamp
			pStringOut		(bool | default=true) 	: Se impostato a vero, il metodo restituisce una data formattata come stringa, atrimenti restituisce la data incapsulata in un oggetto datetime.

		Returns:
			(str | datetime)		: stringa o oggetto datetime rappresentante la data associata al timestamp
		"""

		dt:datetime			= datetime.fromtimestamp(pTimeStamp)

		if (pStringOut == True):
			strDate:str     = dt.strftime("%d-%m-%Y %H:%M")
			return strDate
		else:
			return dt	