"""Pruebas de las piezas base: dinero, validaciones, fechas, periodo y conceptos."""
from datetime import date
from decimal import Decimal

import pytest

from nomina.conceptos import Concepto, TipoConcepto
from nomina.dinero import a_decimal, formatear_pesos, redondear_pesos
from nomina.errores import PorcentajeInvalidoError, ValorNegativoError
from nomina.fechas import sumar_anios, tiene_mas_de
from nomina.periodo import Periodo
from nomina.validaciones import validar_no_negativo, validar_porcentaje


class TestDinero:
    def test_float_se_convierte_sin_arrastrar_error_binario(self):
        assert a_decimal(0.1) + a_decimal(0.2) == Decimal("0.3")

    def test_redondea_al_peso_mas_cercano(self):
        assert redondear_pesos(Decimal("1500.5")) == Decimal("1501")
        assert redondear_pesos(Decimal("1500.4")) == Decimal("1500")

    def test_formato_colombiano(self):
        assert formatear_pesos(3500000) == "$ 3.500.000"


class TestValidaciones:
    def test_cero_es_valido(self):
        assert validar_no_negativo(0, "horas") == 0

    def test_negativo_lanza_error_con_el_campo(self):
        with pytest.raises(ValorNegativoError) as error:
            validar_no_negativo(-1, "horas")
        assert error.value.campo == "horas"

    @pytest.mark.parametrize("valor", [0, "0.04", 1])
    def test_porcentajes_en_rango(self, valor):
        assert validar_porcentaje(valor, "comision") == Decimal(str(valor))

    @pytest.mark.parametrize("valor", [-0.01, 1.5, 4])
    def test_porcentajes_fuera_de_rango(self, valor):
        with pytest.raises(PorcentajeInvalidoError):
            validar_porcentaje(valor, "comision")


class TestFechas:
    def test_exactamente_cinco_anios_no_es_mas_de_cinco(self):
        assert tiene_mas_de(5, date(2021, 10, 31), date(2026, 10, 31)) is False

    def test_un_dia_despues_si_es_mas_de_cinco(self):
        assert tiene_mas_de(5, date(2021, 10, 30), date(2026, 10, 31)) is True

    def test_29_de_febrero_en_anio_no_bisiesto(self):
        assert sumar_anios(date(2024, 2, 29), 1) == date(2025, 2, 28)


class TestPeriodo:
    def test_fecha_corte_es_el_ultimo_dia_del_mes(self):
        assert Periodo(2026, 2).fecha_corte == date(2026, 2, 28)
        assert Periodo(2024, 2).fecha_corte == date(2024, 2, 29)

    def test_mes_invalido(self):
        with pytest.raises(ValueError):
            Periodo(2026, 13)

    def test_nombre_legible(self):
        assert str(Periodo(2026, 10)) == "octubre de 2026"


class TestConcepto:
    def test_redondea_el_valor(self):
        assert Concepto("Bono", Decimal("100.6"), TipoConcepto.DEVENGO).valor == Decimal("101")

    def test_no_acepta_valores_negativos(self):
        with pytest.raises(ValorNegativoError):
            Concepto("Bono", -5, TipoConcepto.DEVENGO)
