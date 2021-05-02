

    
# Module `TimeStampConverter` {#TimeStampConverter}

@author                 :  rscalia
@date               :  Sun 02/05/2021
@last_update            :  Sun 02/05/2021

Questo componente serve per convertire una data in timestamp e viceversa.





    
## Classes


    
### Class `TimeStampConverter` {#TimeStampConverter.TimeStampConverter}




>     class TimeStampConverter










    
#### Methods


    
##### Method `date2Timestamp` {#TimeStampConverter.TimeStampConverter.date2Timestamp}




>     def date2Timestamp(
>         self,
>         pDay: int,
>         pMonth: int,
>         pYear: int,
>         pHour=0,
>         pMinutes=0
>     ) ‑> float


Converte un timestamp UNIX in una Data.


Args
-----=
pDay            (int)   : giorno
pMonth          (int)   : mese
pYear           (int)   : anno
pHour           (int)   : ora
pMinutes        (int)   : minuti

Returns
-----=
<code>float                           </code>
:   timestamp UNIX



    
##### Method `timestamp2Date` {#TimeStampConverter.TimeStampConverter.timestamp2Date}




>     def timestamp2Date(
>         self,
>         pTimeStamp: float,
>         pStringOut=True
>     ) ‑> str


Converte un timestamp UNIX in una Data.


Args
-----=
pTimeStamp              (float) : numero in virgola mobile rappresentante un timestamp
pStringOut              (bool)  : Se impostato a vero, il metodo restituisce una data formattata come stringa, atrimenti restituisce la data incapsulata in un oggetto datetime.

Returns
-----=
(str | datetime)                : stringa o oggetto datetime rappresentante la data associata al timestamp


