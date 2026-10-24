"""Los cuatro tipos de empleado de la empresa."""
from nomina.empleados.asalariado import EmpleadoAsalariado
from nomina.empleados.base import Empleado
from nomina.empleados.por_comision import EmpleadoPorComision
from nomina.empleados.por_horas import EmpleadoPorHoras
from nomina.empleados.temporal import EmpleadoTemporal

__all__ = ["Empleado", "EmpleadoAsalariado", "EmpleadoPorHoras", "EmpleadoPorComision", "EmpleadoTemporal"]
