"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 29/07/2021

Questa classe permette di serializzare e deserializzare i JSON.

Inoltre, la classe aggiunge il supporto alla cifratura ai campi del JSON.
"""

from cryptography.fernet import Fernet
import json
import base64
from os.path            import join
from io                 import BufferedWriter
from typing             import Union
import pickle

class NetworkSerializer (object):

    def __init__ (self, pSecretKeyPath:str="./data/") -> object:
        """
        Costruttore \n

        Args:
            pSecretKeyPath          (str | DEF = "./data/")       : path contenente la chiave di cifratura/decifratura

        """

        self._secretKeyPath:str     = pSecretKeyPath
        self._key:Fernet            = None


    def buildNewKey (self) -> Union[ None , Exception ]:
        """
        Questo metodo genera una nuova chiave crittografica e la salve anche su Disco

        Returns:\n
            Union[ None , Exception ]

        Raises:\n
            Exception       : eccezione da scrittura file da Disco
        """
        self._key:bytes                 = Fernet.generate_key()
        self._cryptEngine:Fernet        = Fernet(self._key)

        #Salvataggio Chiave su Disco
        file_path:str                   = join (self._secretKeyPath, "secret_key.txt")

        try:
            f:BufferedWriter            = open(file_path, "wb")
            f.write(self._key)
            f.close()
        except Exception as exp:
            return exp


    def readKeyFromFile (self) -> Union[ None , Exception ]:
        """ 
        Questo metodo legge la chiave crittografica da disco

        Returns:\n
            Union[ None , Exception ]
        
        Raises:\n
            Exception       : eccezione da lettura file da Disco
        """
        file_path:str                       = join (self._secretKeyPath, "secret_key.txt")

        try:
            self._key:bytes                 = open(file_path, "rb").peek()
        except Exception as exp:
            return exp

        self._cryptEngine:Fernet            = Fernet(self._key)


    def encryptField (self, pField:str) -> Union [ str , Exception ]:
        """
        Questa funzione permette di cifrare una stringa

        Args:\n
            pField              (str)                           : stringa da cifrare

        Returns:\n
                                Union [ str , Exception ]       : crittotesto
        
        Raises:\n
            Exception                                           : eccezione
        """

        #Serializo i dati
        ser_data:str                            = json.dumps(pField)
        encoded_ser_data:bytes                  = ser_data.encode('utf-8')

        try:
            #Cifro Dati
            crypt_text:bytes                    = self._cryptEngine.encrypt(encoded_ser_data)
        except Exception as exp:
            return exp

        #Transformo i dati cifrati in string
        recoded_data:bytes                      = base64.b64encode(crypt_text)  
        crypt_str_data:str                      = recoded_data.decode('ascii')   

        return crypt_str_data


    def decryptField (self, pField:str) -> Union [ str , Exception ]:
        """
        Questa funzione permette di decifrare un crittotesto che era collegato alla cifratura di una stringa

        Args:\n
            pField              (str)                           : crittotesto

        Returns:\n
                                Union [ str , Exception]        : testo in chiaro

        Raises:\n
            Exception                                           : eccezione
        """

        #Trasformo la stringa in dati cifrati
        crypto_text:bytes                           = base64.b64decode(pField)

        try:
            #Decifro i dati
            data:bytes                              = self._cryptEngine.decrypt(crypto_text)
        except Exception as exp:
            return exp
        
        #Deserialize Data
        decrypt_data:str                            = json.loads(data)  

        return decrypt_data  


    def encodeJson (self, pDict:dict) -> bytes:
        """
        Codifica un dizionario in JSON

        Args:\n
            pDict           (dict)      : dizionario da codificare 
        
        Returns:\n
                            (bytes)     : codifica JSON del dizionario
        """
        ser_data:str                = json.dumps(pDict, default=lambda o: o.__dict__, indent=2)
        encoded_ser_data:bytes      = ser_data.encode('utf-8')

        return encoded_ser_data


    def decodeJson (self, pPayLoad:bytes) -> dict:
        """
        Decodifica di un JSON in un dizionario Python

        Args:\n
            pPayLoad        (dict)      : byte rappresentano un JSON
        
        Returns:\n
                            (dict)      : dizionario Python che contiene i dati presenti nel JSON
        """
        deser_data:dict      = json.loads(pPayLoad)

        return deser_data


    def encodeBinaryObj (self , pObject:object) -> bytes:
        """
        Questo metodo permette di serializzare in binario un oggetto Python

        Args:\n
            pObject         (object)        : oggetto da serializzare in binario

        Returns:\n
            bytes                           : oggetto serializzato in binario             
        """
        slob:bytes           = pickle.dumps(obj= pObject) 
        return slob

    
    def decodeBinaryObj (self , pBinObject:bytes) -> object:
        """
        Questo metodo permette di deserializzare un oggetto Python serializzato in binario.

        Args:\n
            pBinObject         (bytes)              : oggetto serializzato in binario

        Returns:\n
            object                                  : oggetto deserializzato             
        """
        obj:object           = pickle.loads( pBinObject )
        return obj

    