"""Reglas de nómina: cada bono, deducción o beneficio es una clase pequeña e intercambiable."""
from nomina.reglas.base import Fase, Regla
from nomina.reglas.beneficios import BonoDeAlimentacion, FondoDeAhorro
from nomina.reglas.bonos import BonoPorAntiguedad, BonoPorVentas
from nomina.reglas.deducciones import DeduccionFija, DeduccionPorcentual

__all__ = ["Fase", "Regla", "BonoPorAntiguedad", "BonoPorVentas", "DeduccionPorcentual",
           "DeduccionFija", "BonoDeAlimentacion", "FondoDeAhorro"]
