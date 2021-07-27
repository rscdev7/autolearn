"""
@author           	:  rscalia
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 25/07/2021

Questo componente serve per testare il domain work del microservizio catalog.
"""
from ..lib.domain_work.worker import get_catalog
import asyncio
import pytest
import pprint


@pytest.mark.asyncio
async def test_domain_work ():
    catalog:Union[ dict , Exception] = await get_catalog()
    assert issubclass ( type(catalog) , Exception) == False

    pprint.pprint (catalog)