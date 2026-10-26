"""Fixtures compartidas por las pruebas."""
import pytest

from nomina.calculadora import CalculadoraNomina


@pytest.fixture
def calculadora():
    return CalculadoraNomina()
