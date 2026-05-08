class MessageDto:
    """Clase DTO para representar un mensaje simple en Redis a través de Sirope."""

    def __init__(self, message_txt: str):
        self._message_txt = message_txt

    @property
    def message_txt(self) -> str:
        """Devuelve el texto del mensaje."""
        return self._message_txt
