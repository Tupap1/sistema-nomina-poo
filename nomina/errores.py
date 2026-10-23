"""Errores propios del dominio de nómina.

Tener errores con nombre propio deja que quien use el sistema sepa exactamente
qué regla se rompió, en vez de recibir un ValueError genérico.
"""


class ErrorNomina(Exception):
    """Error base de todo el sistema de nómina."""


class ValorNegativoError(ErrorNomina, ValueError):
    """Un valor que no puede ser negativo (horas, ventas, salario...) llegó negativo."""

    def __init__(self, campo: str, valor):
        self.campo = campo
        self.valor = valor
        super().__init__(f"El campo '{campo}' no puede ser negativo (llegó {valor}).")


class PorcentajeInvalidoError(ErrorNomina, ValueError):
    """Un porcentaje quedó fuera del rango 0 a 1 (0 % a 100 %)."""

    def __init__(self, campo: str, valor):
        self.campo = campo
        self.valor = valor
        super().__init__(f"El porcentaje '{campo}' debe estar entre 0 y 1 (llegó {valor}).")


class ContratoInvalidoError(ErrorNomina, ValueError):
    """Las fechas del contrato no tienen sentido (por ejemplo, termina antes de empezar)."""


class ContratoNoVigenteError(ErrorNomina):
    """Se intentó liquidar un periodo en el que el contrato no estaba vigente."""


class SalarioNetoNegativoError(ErrorNomina):
    """Las deducciones superaron lo devengado y el neto quedaría negativo."""

    def __init__(self, empleado: str, neto):
        self.empleado = empleado
        self.neto = neto
        super().__init__(f"El salario neto de {empleado} quedaría negativo ({neto}). No se puede liquidar así.")
