"""Presentación en texto de las liquidaciones. Separado del cálculo a propósito (SRP)."""
from decimal import Decimal

from nomina.conceptos import TipoConcepto
from nomina.dinero import formatear_pesos
from nomina.liquidacion import Liquidacion

ANCHO = 68
SECCIONES = (
    (TipoConcepto.DEVENGO, "Devengos", "+"),
    (TipoConcepto.DEDUCCION, "Deducciones", "-"),
    (TipoConcepto.APORTE_AHORRO, "Fondo de ahorro", "-"),
    (TipoConcepto.BENEFICIO, "Beneficios no salariales", "+"),
)


def _linea(texto: str, valor: Decimal, signo: str = "") -> str:
    """Texto a la izquierda y la cifra alineada a la derecha, con el signo en su propia columna."""
    cifra = formatear_pesos(valor).replace("$ ", "")
    return f"{texto:<{ANCHO - 17}}{signo:>2} $ {cifra:>12}"


def desprendible(liquidacion: Liquidacion) -> str:
    """Texto tipo desprendible de pago de un empleado."""
    emp = liquidacion.empleado
    salida = [
        "=" * ANCHO,
        f"{emp.nombre} ({emp.tipo}) · ID {emp.identificacion}",
        f"Periodo: {liquidacion.periodo} · Ingreso: {emp.fecha_ingreso:%d/%m/%Y}",
        "-" * ANCHO,
    ]
    for tipo, titulo, signo in SECCIONES:
        conceptos = liquidacion.conceptos_de(tipo)
        if not conceptos:
            continue
        salida.append(titulo)
        for c in conceptos:
            nombre = f"  {c.nombre}" + (f" ({c.detalle})" if c.detalle else "")
            salida.append(_linea(nombre, c.valor, signo))
    salida += [
        "-" * ANCHO,
        _linea("Salario bruto", liquidacion.salario_bruto),
        _linea("Salario neto", liquidacion.salario_neto),
        _linea("TOTAL A RECIBIR", liquidacion.total_a_recibir),
    ]
    return "\n".join(salida)


def resumen(liquidaciones: list[Liquidacion]) -> str:
    """Tabla corta con el neto de cada empleado y el costo total de la nómina."""
    salida = ["=" * ANCHO, "RESUMEN DE NÓMINA", "-" * ANCHO]
    for liq in liquidaciones:
        salida.append(_linea(f"{liq.empleado.nombre} ({liq.empleado.tipo})", liq.total_a_recibir))
    total = sum((l.total_a_recibir for l in liquidaciones), Decimal("0"))
    salida += ["-" * ANCHO, _linea("Total a pagar", total), "=" * ANCHO]
    return "\n".join(salida)
