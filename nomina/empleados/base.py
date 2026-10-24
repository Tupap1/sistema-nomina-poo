"""Clase base abstracta de todos los empleados."""
from abc import ABC, abstractmethod
from datetime import date

from nomina.conceptos import Concepto
from nomina.fechas import tiene_mas_de
from nomina.periodo import Periodo


class Empleado(ABC):
    """Lo que todo empleado tiene en común: quién es, desde cuándo trabaja y cómo devenga.

    Cada subclase solo responde por lo que gana con su trabajo (devengos).
    Bonos, deducciones y beneficios NO viven aquí: son reglas aparte (ver nomina/reglas).
    """

    def __init__(self, identificacion: str, nombre: str, fecha_ingreso: date):
        if not str(identificacion).strip() or not str(nombre).strip():
            raise ValueError("El empleado necesita identificación y nombre.")
        self._identificacion = str(identificacion).strip()
        self._nombre = str(nombre).strip()
        self._fecha_ingreso = fecha_ingreso

    @property
    def identificacion(self) -> str:
        return self._identificacion

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def fecha_ingreso(self) -> date:
        return self._fecha_ingreso

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Nombre legible del tipo de empleado, para reportes."""

    @abstractmethod
    def devengos(self, periodo: Periodo) -> list[Concepto]:
        """Lo que gana por su trabajo en el periodo, antes de bonos y deducciones."""

    def tiene_mas_de_anios(self, anios: int, periodo: Periodo) -> bool:
        """True si a la fecha de corte del periodo lleva MÁS de 'anios' años en la empresa."""
        return tiene_mas_de(anios, self._fecha_ingreso, periodo.fecha_corte)

    def tiene_contrato_vigente(self, periodo: Periodo) -> bool:
        """Por defecto el contrato es indefinido: vale desde que entró a la empresa."""
        return self._fecha_ingreso <= periodo.fecha_corte

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._identificacion!r}, {self._nombre!r})"
