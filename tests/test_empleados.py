"""Pruebas de cada tipo de empleado: cómo devenga y qué datos rechaza."""
from datetime import date
from decimal import Decimal

import pytest

from nomina.conceptos import TipoConcepto
from nomina.empleados import (Empleado, EmpleadoAsalariado, EmpleadoPorComision,
                              EmpleadoPorHoras, EmpleadoTemporal)
from nomina.errores import ContratoInvalidoError, PorcentajeInvalidoError, ValorNegativoError
from nomina.periodo import Periodo

OCTUBRE = Periodo(2026, 10)
INGRESO = date(2020, 1, 15)


def total(conceptos):
    return sum((c.valor for c in conceptos), Decimal("0"))


def test_empleado_es_abstracto():
    with pytest.raises(TypeError):
        Empleado("1", "Ana", INGRESO)


def test_nombre_e_identificacion_obligatorios():
    with pytest.raises(ValueError):
        EmpleadoAsalariado("", "Ana", INGRESO, 1000)
    with pytest.raises(ValueError):
        EmpleadoAsalariado("1", "  ", INGRESO, 1000)


class TestAsalariado:
    def test_devenga_su_salario_fijo(self):
        emp = EmpleadoAsalariado("1", "Ana", INGRESO, 3_000_000)
        conceptos = emp.devengos(OCTUBRE)
        assert total(conceptos) == 3_000_000
        assert all(c.tipo is TipoConcepto.DEVENGO for c in conceptos)

    def test_salario_negativo_no_se_acepta(self):
        with pytest.raises(ValorNegativoError):
            EmpleadoAsalariado("1", "Ana", INGRESO, -1)


class TestPorHoras:
    def test_hasta_40_horas_no_hay_extra(self):
        emp = EmpleadoPorHoras("2", "Luis", INGRESO, tarifa_hora=20_000, horas_trabajadas=40)
        conceptos = emp.devengos(OCTUBRE)
        assert [c.nombre for c in conceptos] == ["Horas ordinarias"]
        assert total(conceptos) == 800_000

    def test_lo_que_pasa_de_40_se_paga_a_1_5(self):
        emp = EmpleadoPorHoras("2", "Luis", INGRESO, tarifa_hora=20_000, horas_trabajadas=45)
        conceptos = {c.nombre: c.valor for c in emp.devengos(OCTUBRE)}
        assert conceptos["Horas ordinarias"] == 800_000      # 40 h x 20.000
        assert conceptos["Horas extra"] == 150_000           # 5 h x 30.000

    def test_horas_con_decimales(self):
        emp = EmpleadoPorHoras("2", "Luis", INGRESO, tarifa_hora=10_000, horas_trabajadas="42.5")
        assert emp.horas_extra == Decimal("2.5")
        assert total(emp.devengos(OCTUBRE)) == 400_000 + 37_500

    def test_cero_horas_es_valido(self):
        emp = EmpleadoPorHoras("2", "Luis", INGRESO, tarifa_hora=20_000, horas_trabajadas=0)
        assert total(emp.devengos(OCTUBRE)) == 0

    def test_horas_negativas_no_se_aceptan_al_crear(self):
        with pytest.raises(ValorNegativoError) as error:
            EmpleadoPorHoras("2", "Luis", INGRESO, tarifa_hora=20_000, horas_trabajadas=-1)
        assert error.value.campo == "horas_trabajadas"

    def test_horas_negativas_no_se_aceptan_al_actualizar(self):
        emp = EmpleadoPorHoras("2", "Luis", INGRESO, tarifa_hora=20_000, horas_trabajadas=10)
        with pytest.raises(ValorNegativoError):
            emp.horas_trabajadas = -5
        assert emp.horas_trabajadas == 10  # el valor anterior no se dañó


class TestPorComision:
    def test_salario_base_mas_comision(self):
        emp = EmpleadoPorComision("3", "Sara", INGRESO, salario_base=1_500_000,
                                  porcentaje_comision="0.05", ventas=10_000_000)
        conceptos = {c.nombre: c.valor for c in emp.devengos(OCTUBRE)}
        assert conceptos == {"Salario básico": 1_500_000, "Comisión por ventas": 500_000}

    def test_ventas_negativas_no_se_aceptan(self):
        with pytest.raises(ValorNegativoError) as error:
            EmpleadoPorComision("3", "Sara", INGRESO, 1_500_000, "0.05", ventas=-1)
        assert error.value.campo == "ventas"

    def test_ventas_negativas_no_se_aceptan_al_actualizar(self):
        emp = EmpleadoPorComision("3", "Sara", INGRESO, 1_500_000, "0.05", ventas=0)
        with pytest.raises(ValorNegativoError):
            emp.ventas = -100

    def test_porcentaje_de_comision_fuera_de_rango(self):
        with pytest.raises(PorcentajeInvalidoError):
            EmpleadoPorComision("3", "Sara", INGRESO, 1_500_000, 5, ventas=0)  # 5 sería 500 %


class TestTemporal:
    def test_devenga_su_salario_fijo(self):
        emp = EmpleadoTemporal("4", "Juan", date(2026, 7, 1), 2_000_000, date(2026, 12, 31))
        assert total(emp.devengos(OCTUBRE)) == 2_000_000

    def test_contrato_no_puede_terminar_antes_de_empezar(self):
        with pytest.raises(ContratoInvalidoError):
            EmpleadoTemporal("4", "Juan", date(2026, 7, 1), 2_000_000, date(2026, 6, 30))

    def test_vigencia_del_contrato(self):
        emp = EmpleadoTemporal("4", "Juan", date(2026, 7, 1), 2_000_000, date(2026, 10, 15))
        assert emp.tiene_contrato_vigente(Periodo(2026, 10)) is True   # termina a mitad de octubre
        assert emp.tiene_contrato_vigente(Periodo(2026, 11)) is False  # ya terminó
        assert emp.tiene_contrato_vigente(Periodo(2026, 6)) is False   # todavía no empezaba
