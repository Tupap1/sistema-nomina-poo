"""Pruebas de las reglas de negocio del enunciado, pasando por la calculadora completa.

Los valores esperados están hechos a mano en los comentarios para que se pueda
revisar cada número sin correr el código.
ARL: tarifa de riesgo I = 0,522 % del salario bruto.
"""
from datetime import date

import pytest

from nomina.empleados import (EmpleadoAsalariado, EmpleadoPorComision,
                              EmpleadoPorHoras, EmpleadoTemporal)
from nomina.errores import ContratoNoVigenteError
from nomina.periodo import Periodo

OCTUBRE = Periodo(2026, 10)          # fecha de corte: 31 de octubre de 2026
HACE_MAS_DE_5 = date(2020, 3, 1)
EXACTO_5 = date(2021, 10, 31)        # cumple 5 años justo el día de corte
UN_DIA_MAS_DE_5 = date(2021, 10, 30)
EXACTO_1 = date(2025, 10, 31)
UN_DIA_MAS_DE_1 = date(2025, 10, 30)


class TestAsalariado:
    def test_con_mas_de_5_anios_recibe_bono_del_10(self, calculadora):
        emp = EmpleadoAsalariado("1", "Ana", HACE_MAS_DE_5, 3_000_000)
        liq = calculadora.liquidar(emp, OCTUBRE)
        assert liq.valor_de("Bono por antigüedad") == 300_000
        assert liq.salario_bruto == 3_300_000
        assert liq.valor_de("Seguridad social y pensión") == 132_000   # 4 % de 3.300.000
        assert liq.valor_de("ARL") == 17_226                           # 0,522 % de 3.300.000
        assert liq.salario_neto == 3_150_774
        assert liq.valor_de("Bono de alimentación") == 1_000_000
        assert liq.total_a_recibir == 4_150_774

    def test_exactamente_5_anios_todavia_no_recibe_bono(self, calculadora):
        emp = EmpleadoAsalariado("1", "Ana", EXACTO_5, 3_000_000)
        assert calculadora.liquidar(emp, OCTUBRE).valor_de("Bono por antigüedad") == 0

    def test_un_dia_mas_de_5_anios_si_recibe_bono(self, calculadora):
        emp = EmpleadoAsalariado("1", "Ana", UN_DIA_MAS_DE_5, 3_000_000)
        assert calculadora.liquidar(emp, OCTUBRE).valor_de("Bono por antigüedad") == 300_000

    def test_recibe_bono_de_alimentacion_aunque_sea_nuevo(self, calculadora):
        emp = EmpleadoAsalariado("1", "Ana", date(2026, 9, 1), 3_000_000)
        assert calculadora.liquidar(emp, OCTUBRE).valor_de("Bono de alimentación") == 1_000_000


class TestPorHoras:
    def test_extras_deducciones_y_fondo_de_ahorro(self, calculadora):
        emp = EmpleadoPorHoras("2", "Luis", UN_DIA_MAS_DE_1, tarifa_hora=20_000,
                               horas_trabajadas=45, acepta_fondo_ahorro=True)
        liq = calculadora.liquidar(emp, OCTUBRE)
        assert liq.salario_bruto == 950_000                           # 800.000 + 150.000
        assert liq.valor_de("Seguridad social y pensión") == 38_000
        assert liq.valor_de("ARL") == 4_959                           # 4.959,0 redondeado
        assert liq.aporte_fondo_ahorro == 19_000                      # 2 % de 950.000
        assert liq.salario_neto == 888_041

    def test_exactamente_40_horas_no_genera_extra(self, calculadora):
        emp = EmpleadoPorHoras("2", "Luis", HACE_MAS_DE_5, tarifa_hora=20_000, horas_trabajadas=40)
        liq = calculadora.liquidar(emp, OCTUBRE)
        assert liq.valor_de("Horas extra") == 0
        assert liq.salario_bruto == 800_000

    def test_no_recibe_bonos_aunque_tenga_mas_de_5_anios(self, calculadora):
        emp = EmpleadoPorHoras("2", "Luis", HACE_MAS_DE_5, tarifa_hora=20_000, horas_trabajadas=40)
        liq = calculadora.liquidar(emp, OCTUBRE)
        assert liq.valor_de("Bono por antigüedad") == 0
        assert liq.valor_de("Bono de alimentación") == 0

    def test_fondo_requiere_mas_de_un_anio(self, calculadora):
        emp = EmpleadoPorHoras("2", "Luis", EXACTO_1, tarifa_hora=20_000,
                               horas_trabajadas=40, acepta_fondo_ahorro=True)
        assert calculadora.liquidar(emp, OCTUBRE).aporte_fondo_ahorro == 0

    def test_fondo_requiere_que_lo_acepte(self, calculadora):
        emp = EmpleadoPorHoras("2", "Luis", HACE_MAS_DE_5, tarifa_hora=20_000,
                               horas_trabajadas=40, acepta_fondo_ahorro=False)
        assert calculadora.liquidar(emp, OCTUBRE).aporte_fondo_ahorro == 0

    def test_sin_horas_el_neto_es_cero_y_no_negativo(self, calculadora):
        emp = EmpleadoPorHoras("2", "Luis", HACE_MAS_DE_5, tarifa_hora=20_000, horas_trabajadas=0)
        assert calculadora.liquidar(emp, OCTUBRE).salario_neto == 0


class TestPorComision:
    def test_ventas_sobre_20_millones_dan_bono_del_3(self, calculadora):
        emp = EmpleadoPorComision("3", "Sara", HACE_MAS_DE_5, salario_base=1_500_000,
                                  porcentaje_comision="0.05", ventas=25_000_000)
        liq = calculadora.liquidar(emp, OCTUBRE)
        assert liq.valor_de("Comisión por ventas") == 1_250_000
        assert liq.valor_de("Bono por ventas") == 750_000            # 3 % de 25.000.000
        assert liq.salario_bruto == 3_500_000
        assert liq.valor_de("Seguridad social y pensión") == 140_000
        assert liq.valor_de("ARL") == 18_270
        assert liq.salario_neto == 3_341_730
        assert liq.total_a_recibir == 4_341_730                      # + bono de alimentación

    def test_exactamente_20_millones_no_da_bono(self, calculadora):
        emp = EmpleadoPorComision("3", "Sara", HACE_MAS_DE_5, 1_500_000, "0.05", ventas=20_000_000)
        assert calculadora.liquidar(emp, OCTUBRE).valor_de("Bono por ventas") == 0

    def test_un_peso_sobre_20_millones_si_da_bono(self, calculadora):
        emp = EmpleadoPorComision("3", "Sara", HACE_MAS_DE_5, 1_500_000, "0.05", ventas=20_000_001)
        assert calculadora.liquidar(emp, OCTUBRE).valor_de("Bono por ventas") == 600_000

    def test_no_tiene_bono_de_antiguedad(self, calculadora):
        emp = EmpleadoPorComision("3", "Sara", HACE_MAS_DE_5, 1_500_000, "0.05", ventas=0)
        assert calculadora.liquidar(emp, OCTUBRE).valor_de("Bono por antigüedad") == 0


class TestTemporal:
    def test_solo_salario_y_deducciones(self, calculadora):
        emp = EmpleadoTemporal("4", "Juan", HACE_MAS_DE_5, 2_000_000, date(2026, 12, 31))
        liq = calculadora.liquidar(emp, OCTUBRE)
        assert liq.salario_bruto == 2_000_000
        assert liq.total_deducciones == 80_000 + 10_440
        assert liq.beneficios_no_salariales == 0
        assert liq.aporte_fondo_ahorro == 0
        assert liq.salario_neto == 1_909_560
        assert liq.total_a_recibir == liq.salario_neto

    def test_no_se_liquida_fuera_del_contrato(self, calculadora):
        emp = EmpleadoTemporal("4", "Juan", date(2026, 1, 1), 2_000_000, date(2026, 9, 30))
        with pytest.raises(ContratoNoVigenteError):
            calculadora.liquidar(emp, OCTUBRE)


def test_no_se_liquida_a_alguien_que_todavia_no_ha_entrado(calculadora):
    emp = EmpleadoAsalariado("1", "Ana", date(2026, 11, 3), 3_000_000)
    with pytest.raises(ContratoNoVigenteError):
        calculadora.liquidar(emp, OCTUBRE)


def test_liquidar_todos(calculadora):
    empleados = [
        EmpleadoAsalariado("1", "Ana", HACE_MAS_DE_5, 3_000_000),
        EmpleadoTemporal("4", "Juan", HACE_MAS_DE_5, 2_000_000, date(2026, 12, 31)),
    ]
    liquidaciones = calculadora.liquidar_todos(empleados, OCTUBRE)
    assert [l.empleado.nombre for l in liquidaciones] == ["Ana", "Juan"]
