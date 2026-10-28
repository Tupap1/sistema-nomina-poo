"""Qué reglas le aplican a cada tipo de empleado."""
from nomina.empleados.base import Empleado
from nomina.reglas.base import Regla


class PoliticaNomina:
    """Arma la lista de reglas de un empleado: las comunes a todos más las de su tipo.

    La política no calcula nada; solo responde "a este empleado le aplican estas reglas".
    """

    def __init__(self, reglas_comunes: list[Regla] | None = None):
        self._reglas_comunes = list(reglas_comunes or [])
        self._reglas_por_tipo: dict[type, list[Regla]] = {}

    def registrar(self, tipo_empleado: type, *reglas: Regla) -> "PoliticaNomina":
        """Agrega reglas para un tipo. Devuelve la misma política para poder encadenar."""
        self._reglas_por_tipo.setdefault(tipo_empleado, []).extend(reglas)
        return self

    def reglas_para(self, empleado: Empleado) -> list[Regla]:
        reglas = list(self._reglas_comunes)
        # Se recorre el MRO para que una subclase herede las reglas de su clase padre.
        for clase in type(empleado).__mro__:
            reglas.extend(self._reglas_por_tipo.get(clase, []))
        return reglas
