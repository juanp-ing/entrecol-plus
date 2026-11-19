"""Piezas comunes del ETL (RF-08 a RF-10)."""
from dataclasses import dataclass, field


class ErrorEstructura(Exception):
    """El archivo no tiene la estructura esperada: se revierte toda la carga."""


@dataclass
class Resumen:
    origen: str
    leidos: int = 0
    insertados: int = 0
    actualizados: int = 0
    rechazados: list[dict] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def rechazar(self, fila: int | str, motivo: str) -> None:
        self.rechazados.append({"registro": fila, "motivo": motivo})

    def contar(self, filas_afectadas: int) -> None:
        """MariaDB con ON DUPLICATE KEY UPDATE devuelve 1 si inserto, 2 si actualizo y 0 si no cambio."""
        if filas_afectadas == 1:
            self.insertados += 1
        elif filas_afectadas == 2:
            self.actualizados += 1

    def como_dict(self) -> dict:
        return {
            "origen": self.origen,
            "leidos": self.leidos,
            "insertados": self.insertados,
            "actualizados": self.actualizados,
            "sin_cambios": self.leidos - self.insertados - self.actualizados - len(self.rechazados),
            "rechazados": len(self.rechazados),
            "detalle_rechazos": self.rechazados[:500],
            "avisos": self.avisos,
        }


def id_catalogo(cur, cache: dict, tabla: str, pk: str, col: str, valor: str) -> int:
    """Devuelve el id de un valor de catalogo, insertandolo si no existe (idempotente)."""
    if valor in cache:
        return cache[valor]
    cur.execute(f"SELECT {pk} FROM {tabla} WHERE {col} = %s", (valor,))
    fila = cur.fetchone()
    if fila:
        cache[valor] = fila[pk]
    else:
        cur.execute(f"INSERT INTO {tabla} ({col}) VALUES (%s)", (valor,))
        cache[valor] = cur.lastrowid
    return cache[valor]
