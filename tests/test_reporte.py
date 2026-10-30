"""Pruebas de la presentación y de que el demo corre de punta a punta."""
from datetime import date

from main import empleados_de_ejemplo, main
from nomina.empleados import EmpleadoTemporal
from nomina.periodo import Periodo
from nomina.reporte import desprendible, resumen


def test_desprendible_muestra_conceptos_y_totales(calculadora):
    emp = EmpleadoTemporal("4", "Juan", date(2026, 7, 1), 2_000_000, date(2026, 12, 31))
    texto = desprendible(calculadora.liquidar(emp, Periodo(2026, 10)))
    assert "Juan (Temporal)" in texto
    assert "Salario básico" in texto
    assert "1.909.560" in texto
    assert "Beneficios" not in texto  # el temporal no tiene beneficios


def test_resumen_suma_el_total_de_la_nomina(calculadora):
    liquidaciones = calculadora.liquidar_todos(empleados_de_ejemplo(), Periodo(2026, 10))
    total = sum(l.total_a_recibir for l in liquidaciones)
    assert f"{int(total):,}".replace(",", ".") in resumen(liquidaciones)


def test_el_demo_corre_sin_errores(capsys):
    main()
    salida = capsys.readouterr().out
    assert "RESUMEN DE NÓMINA" in salida
    assert "Horas negativas: rechazado" in salida
