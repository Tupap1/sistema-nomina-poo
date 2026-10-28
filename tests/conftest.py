"""Fixtures compartidas por las pruebas."""
import pytest

from nomina.configuracion import crear_calculadora


@pytest.fixture
def calculadora():
    return crear_calculadora()
