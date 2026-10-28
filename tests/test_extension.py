"""Pruebas del diseño: reglas inyectables, tipos nuevos sin tocar la calculadora y neto no negativo."""
import inspect
from datetime import date

import pytest

import nomina.calculadora as modulo_calculadora
from nomina.calculadora import CalculadoraNomina
from nomina.conceptos import Concepto, TipoConcepto
from nomina.configuracion import crear_calculadora, politica_por_defecto
from nomina.empleados import Empleado, EmpleadoAsalariado
from nomina.errores import SalarioNetoNegativoError
from nomina.periodo import Periodo
from nomina.politica import PoliticaNomina
from nomina.reglas import BonoPorAntiguedad, DeduccionFija, DeduccionPorcentual

OCTUBRE = Periodo(2026, 10)
ANTIGUO = date(2015, 1, 1)


class TestSalarioNetoNoNegativo:
    def test_deducciones_mayores_al_bruto_lanzan_error(self):
        politica = politica_por_defecto().registrar(EmpleadoAsalariado, DeduccionFija("Embargo", 5_000_000))
        emp = EmpleadoAsalariado("1", "Ana", date(2026, 1, 1), 1_000_000)
        with pytest.raises(SalarioNetoNegativoError) as error:
            CalculadoraNomina(politica).liquidar(emp, OCTUBRE)
        assert error.value.empleado == "Ana"
        assert error.value.neto < 0

    def test_neto_exactamente_cero_si_se_permite(self):
        politica = PoliticaNomina([DeduccionFija("Libranza", 1_000_000)])
        emp = EmpleadoAsalariado("1", "Ana", date(2026, 1, 1), 1_000_000)
        assert CalculadoraNomina(politica).liquidar(emp, OCTUBRE).salario_neto == 0

    def test_el_bono_de_alimentacion_no_tapa_un_neto_negativo(self):
        # Aunque el total a recibir quedaría positivo por el bono, el SALARIO neto no puede ser negativo.
        politica = politica_por_defecto().registrar(EmpleadoAsalariado, DeduccionFija("Embargo", 1_100_000))
        emp = EmpleadoAsalariado("1", "Ana", date(2026, 1, 1), 1_000_000)
        with pytest.raises(SalarioNetoNegativoError):
            CalculadoraNomina(politica).liquidar(emp, OCTUBRE)


class Practicante(Empleado):
    """Tipo nuevo que no existe en el sistema: sirve para probar que se puede extender."""

    def __init__(self, identificacion, nombre, fecha_ingreso, apoyo):
        super().__init__(identificacion, nombre, fecha_ingreso)
        self._apoyo = apoyo

    @property
    def tipo(self):
        return "Practicante"

    def devengos(self, periodo):
        return [Concepto("Apoyo de sostenimiento", self._apoyo, TipoConcepto.DEVENGO)]


class TestAbiertoACambios:
    def test_tipo_nuevo_sin_tocar_la_calculadora(self):
        politica = PoliticaNomina().registrar(Practicante, DeduccionPorcentual("ARL", "0.00522"))
        liq = CalculadoraNomina(politica).liquidar(Practicante("9", "Mario", date(2026, 8, 1), 1_000_000), OCTUBRE)
        assert liq.salario_bruto == 1_000_000
        assert liq.valor_de("ARL") == 5_220

    def test_una_subclase_hereda_las_reglas_de_su_padre(self):
        class AsalariadoDirectivo(EmpleadoAsalariado):
            pass

        liq = crear_calculadora().liquidar(AsalariadoDirectivo("1", "Ana", ANTIGUO, 5_000_000), OCTUBRE)
        assert liq.valor_de("Bono por antigüedad") == 500_000
        assert liq.valor_de("Bono de alimentación") == 1_000_000

    def test_la_tarifa_de_arl_se_puede_cambiar(self):
        emp = EmpleadoAsalariado("1", "Ana", date(2026, 1, 1), 1_000_000)
        assert crear_calculadora(tarifa_arl="0.01044").liquidar(emp, OCTUBRE).valor_de("ARL") == 10_440

    def test_las_deducciones_se_aplican_despues_de_los_bonos_sin_importar_el_orden_de_registro(self):
        politica = PoliticaNomina().registrar(
            EmpleadoAsalariado,
            DeduccionPorcentual("Seguridad social y pensión", "0.04"),  # registrada primero
            BonoPorAntiguedad("0.10", 5),
        )
        liq = CalculadoraNomina(politica).liquidar(EmpleadoAsalariado("1", "Ana", ANTIGUO, 3_000_000), OCTUBRE)
        assert liq.valor_de("Seguridad social y pensión") == 132_000  # 4 % de 3.300.000, no de 3.000.000


def test_la_calculadora_no_conoce_los_tipos_concretos():
    fuente = inspect.getsource(modulo_calculadora)
    for tipo in ("EmpleadoAsalariado", "EmpleadoPorHoras", "EmpleadoPorComision", "EmpleadoTemporal", "isinstance"):
        assert tipo not in fuente
