"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questo componente permette di testare il componente NetworkSerializer
"""

from ..lib.network_serializer.NetworkSerializer import NetworkSerializer


KEY_PATH:str        = "../data/"
READ_FROM_DISK:bool = True
DATA_TO_CYPHER:str  = "Test di cifratura Sim"
DATA:dict           = {"ciao":450 , "test":"test", "jhg":[4,5,8,7]}


def test_nt_ser():
    ns:NetworkSerializer = NetworkSerializer(KEY_PATH)

    if (READ_FROM_DISK == False):
        ns.buildNewKey()
    else:
        ns.readKeyFromFile()

    res:str     = ns.encryptField(DATA_TO_CYPHER)
    res:str     = ns.decryptField(res)

    print ("\n[!] Dati decifrati: {}".format(res))
    assert DATA_TO_CYPHER == res


def test_json_encoding ():
    ns:NetworkSerializer = NetworkSerializer()

    encoded_data:bytes = ns.encodeJson(DATA)

    decoded_data:dict  = ns.decodeJson(encoded_data)

    print ("\n[!] Dati Decodificati: {}".format(decoded_data))

    assert decoded_data == DATA