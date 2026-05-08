"""Clase DTO para representar una Transacción económica."""

class TransactionDto:
    """Transacción individual asociada a una cuenta y categoría."""

    def __init__(self, amount: float, notes: str, date_str: str, 
                 cat_oid: str, acc_oid: str, user_oid: str):
        self._amount = float(amount)
        self._notes = notes
        self._date_str = date_str
        self._cat_oid = cat_oid
        self._acc_oid = acc_oid
        self._user_oid = user_oid

    @property
    def amount(self) -> float:
        """Monto de la transacción. Positivo = Ingreso, Negativo = Gasto."""
        return self._amount

    @property
    def notes(self) -> str:
        """Notas o descripción de la transacción."""
        return self._notes

    @property
    def date_str(self) -> str:
        """Fecha en formato YYYY-MM-DD."""
        return self._date_str

    @property
    def cat_oid(self) -> str:
        """OID de la Categoría asociada."""
        return self._cat_oid

    @property
    def acc_oid(self) -> str:
        """OID de la Cuenta asociada."""
        return self._acc_oid

    @property
    def user_oid(self) -> str:
        """OID del usuario propietario."""
        return self._user_oid
