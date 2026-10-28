"""Punto de composición: el único lugar que conoce los tipos concretos y sus reglas.

Si cambia un porcentaje o llega un tipo de empleado nuevo, se toca aquí y no la calculadora.
"""
from decimal import Decimal

from nomina.calculadora import CalculadoraNomina
from nomina.empleados import (EmpleadoAsalariado, EmpleadoPorComision,
                              EmpleadoPorHoras, EmpleadoTemporal)
from nomina.politica import PoliticaNomina
from nomina.reglas import (BonoDeAlimentacion, BonoPorAntiguedad, BonoPorVentas,
                           DeduccionPorcentual, FondoDeAhorro)

PORCENTAJE_SEGURIDAD_SOCIAL = Decimal("0.04")
# Supuesto: el enunciado no da la tarifa de ARL. Se usa la del riesgo I (oficinas), 0,522 %.
TARIFA_ARL_RIESGO_I = Decimal("0.00522")


def politica_por_defecto(tarifa_arl=TARIFA_ARL_RIESGO_I) -> PoliticaNomina:
    """Las reglas del enunciado, tipo por tipo."""
    politica = PoliticaNomina(reglas_comunes=[
        DeduccionPorcentual("Seguridad social y pensión", PORCENTAJE_SEGURIDAD_SOCIAL),
        DeduccionPorcentual("ARL", tarifa_arl),
    ])
    bono_alimentacion = BonoDeAlimentacion(1_000_000)
    politica.registrar(EmpleadoAsalariado, BonoPorAntiguedad("0.10", anios_minimos=5), bono_alimentacion)
    politica.registrar(EmpleadoPorComision, BonoPorVentas(20_000_000, "0.03"), bono_alimentacion)
    politica.registrar(EmpleadoPorHoras, FondoDeAhorro("0.02", anios_minimos=1))
    politica.registrar(EmpleadoTemporal)  # sin bonos ni beneficios adicionales
    return politica


def crear_calculadora(tarifa_arl=TARIFA_ARL_RIESGO_I) -> CalculadoraNomina:
    return CalculadoraNomina(politica_por_defecto(tarifa_arl))
