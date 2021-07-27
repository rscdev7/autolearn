"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente realizza la computazione di dominio associata al microservizio Catalog.
"""

import aiofiles
import json
import os
from typing         import Union


async def get_catalog () -> Union[ dict , Exception]:
    """
    # **get_catalog**
    
    Questa funzione realizza la computazione di dominio del microservizio catalog.
    """

    #Path file catalogo
    current_dir                         = os.getcwd().split("/")[-1]

    #Localizzazione esecuzione al livello di path
    if (current_dir == "test"):
        path:str                        = os.path.join ( "..", "data" , "autolearn_catalog.json" )
    else:
        path:str                        = os.path.join ( "data" , "autolearn_catalog.json" )


    #Recupero Catalogo da Disco
    try:
        async with aiofiles.open (path) as fl_descriptor:
            raw_data:bytes              = await fl_descriptor.read()
            catalog:dict                = json.loads(raw_data)
            return catalog
    except Exception as exp:
        return exp