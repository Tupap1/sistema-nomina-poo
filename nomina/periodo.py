"""El periodo que se liquida. La nómina de este sistema es mensual."""
import calendar
from dataclasses import dataclass
from datetime import date

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre")


@dataclass(frozen=True)
class Periodo:
    """Un mes de nómina. La antigüedad se mide a la fecha de corte (último día del mes)."""

    anio: int
    mes: int

    def __post_init__(self):
        if not 1 <= self.mes <= 12:
            raise ValueError(f"El mes debe estar entre 1 y 12 (llegó {self.mes}).")

    @property
    def inicio(self) -> date:
        return date(self.anio, self.mes, 1)

    @property
    def fecha_corte(self) -> date:
        ultimo_dia = calendar.monthrange(self.anio, self.mes)[1]
        return date(self.anio, self.mes, ultimo_dia)

    def __str__(self) -> str:
        return f"{MESES[self.mes - 1]} de {self.anio}"
