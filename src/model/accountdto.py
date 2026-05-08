"""Clase DTO para representar una Cuenta bancaria o fondo."""

class AccountDto:
    """Cuenta que agrupa transacciones y tiene un saldo."""

    def __init__(self, name: str, initial_balance: float, user_oid: str):
        self._name = name
        self._initial_balance = float(initial_balance)
        self._user_oid = user_oid

    @property
    def name(self) -> str:
        """Nombre de la cuenta."""
        return self._name

    @property
    def initial_balance(self) -> float:
        """Saldo inicial al crear la cuenta."""
        return self._initial_balance

    @property
    def user_oid(self) -> str:
        """OID del usuario propietario."""
        return self._user_oid
