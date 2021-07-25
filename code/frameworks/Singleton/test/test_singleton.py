"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente serve per testare il design pattern Singleton.

"""

from ..lib.singleton.Singleton import Singleton


class SingletonClass (metaclass=Singleton):

    def __init__(self, pArg1:int , pArg2:str):
        self._arg1:int  = pArg1
        self._arg2:str  = pArg2

    def print (self) -> None:
        print ("[!] Arg 1: {}".format(self._arg1))
        print ("[!] Arg 2: {}".format(self._arg2))


def test_singleton():

    obj_1:SingletonClass   = SingletonClass(100 , "test1")
    print ("\n[!] STAMPA PRIMO OGGETTO \n")
    obj_1.print()

    
    obj_2:SingletonClass   = SingletonClass(5000 , "test2")
    assert obj_1._arg1 == obj_2._arg1 and obj_1._arg2 == obj_2._arg2
    print ("\n[!] STAMPA SECONDO OGGETTO \n")
    obj_2.print()
    