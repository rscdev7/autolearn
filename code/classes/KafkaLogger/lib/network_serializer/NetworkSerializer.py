"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questa classe permette di serializzare e deserializzare i JSON.

Inoltre, la classe aggiunge il supporto alla cifratura ai campi del JSON.
"""

from cryptography.fernet import Fernet
import json
import base64
from os.path            import join
from io                 import BufferedWriter


class NetworkSerializer (object):

    def __init__ (self, pSecretKeyPath:str="./data/") -> object:
        """
        Costruttore \n

        Args:
            pSecretKeyPath          (str)       : path contenente la chiave di cifratura/decifratura

        """

        self._secretKeyPath:str     = pSecretKeyPath
        self._key:Fernet            = None


    def buildNewKey (self) -> None:
        """
        Questo metodo genera una nuova chiave crittografica e la salve anche su Disco
        """
        self._key:bytes                 = Fernet.generate_key()
        self._cryptEngine:Fernet        = Fernet(self._key)

        #Salvataggio Chiave su Disco
        file_path:str                   = join (self._secretKeyPath, "secret_key.txt")
        f:BufferedWriter                = open(file_path, "wb")

        f.write(self._key)
        f.close()


    def readKeyFromFile (self) -> None:
        """ 
        Questo metodo legge la chiave crittografica da disco
        """
        file_path:str                   = join (self._secretKeyPath, "secret_key.txt")

        self._key:bytes                 = open(file_path, "rb").peek()
        self._cryptEngine:Fernet        = Fernet(self._key)


    def encryptField (self, pField:str) -> str:
        """
        Questa funzione permette di cifrare una stringa

        Args:
            pField              (str)       : stringa da cifrare

        Returns:
                                (str)       : crittotesto
        """

        #Serializo i dati
        ser_data:str                            = json.dumps(pField)
        encoded_ser_data:bytes                  = ser_data.encode('utf-8')

        #Cifro Dati
        crypt_text:bytes                        = self._cryptEngine.encrypt(encoded_ser_data)

        #Transformo i dati cifrati in string
        recoded_data:bytes                      = base64.b64encode(crypt_text)  
        crypt_str_data:str                      = recoded_data.decode('ascii')   

        return crypt_str_data


    def decryptField (self, pField:str) -> str:
        """
        Questa funzione permette di decifrare un crittotesto che era collegato alla cifratura di una stringa

        Args:
            pField              (str)       : crittotesto

        Returns:
                                (str)       : testo in chiaro
        """

        #Trasformo la stringa in dati cifrati
        crypto_text:bytes                       = base64.b64decode(pField)

        #Decifro i dati
        data:bytes                              = self._cryptEngine.decrypt(crypto_text)

        #Deserialize Data
        decrypt_data:str                        = json.loads(data)  
        
        return decrypt_data  


    def encodeJson (self, pDict:dict) -> bytes:
        """
        Codifica un dizionario in JSON

        Args:
            pDict           (dict)      : dizionario da codificare 
        
        Returns:
                            (bytes)     : codifica JSON del dizionario
        """
        ser_data:str                = json.dumps(pDict, default=lambda o: o.__dict__, indent=2)
        encoded_ser_data:bytes      = ser_data.encode('utf-8')

        return encoded_ser_data


    def decodeJson (self, pPayLoad:bytes) -> dict:
        """
        Decodifica di un JSON in un dizionario Python

        Args:
            pPayLoad        (dict)      : byte rappresentano un JSON
        
        Returns:
                            (dict)      : dizionario Python che contiene i dati presenti nel JSON
        """
        deser_data:dict      = json.loads(pPayLoad)

        return deser_data

    