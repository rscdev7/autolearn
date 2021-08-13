"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 12/08/2021                       \n
@last-update            :  Fri 13/08/2021                       \n

Questo componente implementa l'input da tastiera asincrono comprensivo di controllo di tipo
"""

import sys
import asyncio
from typing                 import Union


async def ainput(pGuide: str) -> str:
    """
    # **ainput**

    Questa funzione permette di prelevare un input da tastiera in maniera asincrona

    Args:\n
        pGuide          (str)           : messaggio che guida l'utente nell'inserire un valore valido

    Returns:\n
        str
    """
    await asyncio.get_event_loop().run_in_executor( None , lambda s = pGuide : sys.stdout.write( s+"\n>> " ) )
    usr_input:str                       = await asyncio.get_event_loop().run_in_executor( None , sys.stdin.readline )
    return usr_input.strip('\n')


async def int_input ( pGuide:str ) -> Union[ int , Exception ]:
    """
    # **int_input**

    Questa funzione permette di effettuare un input da tastiera di numeri interi

    Args:\n
        pGuide          (str)           : messaggio che guida l'utente nell'inserire un valore valido

    Returns:\n
        Union[ int , Exception ]

    Raises:\n
        Exception                       : errore nel cast dell'input da tastiera
    """
    keyboard_out:str        = await ainput(pGuide)
    try:
        usr_input:int       = int( keyboard_out )
    except Exception as exp:
        return exp

    return usr_input


async def float_input ( pGuide:str ) -> Union[ float , Exception ]:
    """
    # **float_input**

    Questa funzione permette di effettuare un input da tastiera di numeri in virgola mobile

    Args:\n
        pGuide          (str)           : messaggio che guida l'utente nell'inserire un valore valido

    Returns:\n
        Union[ float , Exception ]

    Raises:\n
        Exception                       : errore nel cast dell'input da tastiera
    """
    keyboard_out:str        = await ainput(pGuide)
    try:
        usr_input:float     = float( keyboard_out )
    except Exception as exp:
        return exp

    return usr_input


async def str_input ( pGuide:str ) -> str:
    """
    # **str_input**

    Questa funzione permette di effettuare un input da tastiera di tipo stringa

    Args:\n
        pGuide          (str)           : messaggio che guida l'utente nell'inserire un valore valido

    Returns:\n
        str
    """
    keyboard_out:str        = await ainput(pGuide)
    return keyboard_out


async def bool_input ( pGuide:str ) -> Union[ bool , Exception ]:
    """
    # **bool_input**

    Questa funzione permette di effettuare un input da tastiera di valori booleani

    Args:\n
        pGuide          (str)           : messaggio che guida l'utente nell'inserire un valore valido

    Returns:\n
        Union[ bool , Exception ]

    Raises:\n
        Exception                       : errore nel cast dell'input da tastiera
    """
    keyboard_out:str        = await ainput(pGuide)

    try:
        usr_input:bool      = True if int(keyboard_out) == 1 else False
    except Exception as exp:
        return exp

    return usr_input


async def selection_input ( pGuide:str , pNOps:int ) -> Union[ int , Exception ]:
    """
    # **selection_input**

    Questa funzione permette di far scegliere all'utente un'opzione su un apposita lista numerata a cominciare da 1

    Args:\n
        pGuide          (str)           : messaggio che guida l'utente nell'inserire un valore valido
        pNOps           (int)           : numero opzioni lista

    Returns:\n
        Union[ int , Exception ]

    Raises:\n
        Exception                       : errore nel cast dell'input da tastiera oppure opzione scelta non valida
    """
    keyboard_out:str        = await ainput(pGuide)

    try:
        usr_choice:int      = int ( keyboard_out )

        if usr_choice < 1 or usr_choice > pNOps:
            raise ValueError("[!] L'opzione scelta è inesistente")

    except Exception as exp:
        if "[!]" in str(exp):
            return exp 
        else:
            return TypeError("Errore nel tipo di dato inserito")


    return usr_choice
