"""Clase DTO para representar un Presupuesto mensual por categoría."""

class BudgetDto:
    """Presupuesto mensual asociado a una categoría de gasto."""

    def __init__(self, cat_oid: str, limit_amount: float, user_oid: str = ""):
        self._cat_oid = cat_oid
        self._limit_amount = limit_amount
        self._user_oid = user_oid

    @property
    def cat_oid(self) -> str:
        """OID de la categoría asociada."""
        return self._cat_oid

    @property
    def limit_amount(self) -> float:
        """Límite mensual de gasto en euros."""
        return self._limit_amount

    @limit_amount.setter
    def limit_amount(self, value: float):
        self._limit_amount = value

    @property
    def user_oid(self) -> str:
        """OID del usuario propietario."""
        return self._user_oid
