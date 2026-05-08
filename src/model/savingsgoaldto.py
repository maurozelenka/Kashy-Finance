"""Clase DTO para representar una Meta de Ahorro."""

class SavingsGoalDto:
    """Meta de ahorro con objetivo y progreso."""

    def __init__(self, name: str, target_amount: float, current_amount: float = 0.0, 
                 icon: str = "savings", color: str = "#ca98ff", user_oid: str = ""):
        self._name = name
        self._target_amount = target_amount
        self._current_amount = current_amount
        self._icon = icon
        self._color = color
        self._user_oid = user_oid

    @property
    def name(self) -> str:
        """Nombre de la meta."""
        return self._name

    @property
    def target_amount(self) -> float:
        """Cantidad objetivo en euros."""
        return self._target_amount

    @property
    def current_amount(self) -> float:
        """Cantidad ahorrada hasta ahora."""
        return self._current_amount

    @current_amount.setter
    def current_amount(self, value: float):
        self._current_amount = value

    @property
    def icon(self) -> str:
        """Icono de Material Symbols."""
        return self._icon

    @property
    def color(self) -> str:
        """Color de la meta."""
        return self._color

    @property
    def user_oid(self) -> str:
        """OID del usuario propietario."""
        return self._user_oid

    @property
    def progress(self) -> float:
        """Porcentaje de progreso (0-100)."""
        if self._target_amount <= 0:
            return 0
        return min((self._current_amount / self._target_amount) * 100, 100)
