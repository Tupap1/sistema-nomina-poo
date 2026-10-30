"""Demo del sistema de nómina: liquida octubre de 2026 para un empleado de cada tipo.

Uso:  python main.py
"""
from datetime import date

from nomina.configuracion import crear_calculadora
from nomina.empleados import (EmpleadoAsalariado, EmpleadoPorComision,
                              EmpleadoPorHoras, EmpleadoTemporal)
from nomina.errores import ErrorNomina
from nomina.periodo import Periodo
from nomina.reporte import desprendible, resumen


def empleados_de_ejemplo():
    return [
        EmpleadoAsalariado("1001", "Ana Gómez", date(2019, 3, 1), salario_mensual=3_000_000),
        EmpleadoAsalariado("1002", "Pedro Ruiz", date(2024, 2, 1), salario_mensual=2_500_000),
        EmpleadoPorHoras("1003", "Luis Mejía", date(2024, 6, 10), tarifa_hora=20_000,
                         horas_trabajadas=45, acepta_fondo_ahorro=True),
        EmpleadoPorComision("1004", "Sara Díaz", date(2022, 8, 16), salario_base=1_500_000,
                            porcentaje_comision="0.05", ventas=25_000_000),
        EmpleadoTemporal("1005", "Juan Pérez", date(2026, 7, 1), salario_mensual=2_000_000,
                         fecha_fin_contrato=date(2026, 12, 31)),
    ]


def mostrar_validaciones():
    """Muestra que las reglas de validación del enunciado sí se cumplen."""
    print("\nVALIDACIONES")
    intentos = [
        ("Horas negativas", lambda: EmpleadoPorHoras("9", "X", date(2025, 1, 1), 20_000, horas_trabajadas=-3)),
        ("Ventas negativas", lambda: EmpleadoPorComision("9", "X", date(2025, 1, 1), 1_000_000, "0.05", ventas=-1)),
    ]
    for descripcion, intento in intentos:
        try:
            intento()
        except ErrorNomina as error:
            print(f"  {descripcion}: rechazado -> {error}")


def main():
    periodo = Periodo(2026, 10)
    calculadora = crear_calculadora()
    liquidaciones = calculadora.liquidar_todos(empleados_de_ejemplo(), periodo)
    for liquidacion in liquidaciones:
        print(desprendible(liquidacion))
    print(resumen(liquidaciones))
    mostrar_validaciones()


if __name__ == "__main__":
    main()
