"""Clase DTO para representar una Categoría de ingresos/gastos."""

class CategoryDto:
    """Categoría para clasificar las transacciones."""

    def __init__(self, name: str, cat_type: str, color: str = "#000000", user_oid: str = "", icon: str = "category"):
        self._name = name
        self._cat_type = cat_type # 'ingreso' o 'gasto'
        self._color = color
        self._user_oid = user_oid
        self._icon = icon

    @property
    def name(self) -> str:
        """Nombre de la categoría."""
        return self._name

    @property
    def cat_type(self) -> str:
        """Tipo de categoría: 'ingreso' o 'gasto'."""
        return self._cat_type

    @property
    def color(self) -> str:
        """Color asignado a la categoría."""
        return self._color

    @property
    def user_oid(self) -> str:
        """OID del usuario propietario."""
        return self._user_oid

    @property
    def icon(self) -> str:
        """Icono (Material Symbol) asociado a la categoría."""
        # Manejo retrocompatible: si es un emoji, devolvemos un icono por defecto
        val = getattr(self, "_icon", "category")
        if len(val) <= 2: # Probablemente un emoji
            return "category"
        return val
