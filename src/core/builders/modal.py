from typing import Any, Self
from uuid import uuid4

from disnake import ModalInteraction
from disnake.ui import Modal, TextInput


class ModalBuilder:
    def __init__(self) -> None:
        self._fields: dict[str, Any] = {
            "components": []
        }

    def set_title(self, title: str) -> Self:
        self._fields["title"] = title
        return self

    def set_callback(self, callback: Any) -> Self:
        self._fields["callback"] = callback
        return self

    def add_component(self, component: TextInput) -> Self:
        self._fields["components"].append(component)
        return self

    def set_timeout(self, timeout: int | float) -> Self:
        self._fields["timeout"] = timeout
        return self

    def build(self, custom_id: str | None = None) -> Modal:
        if custom_id is None:
            custom_id = uuid4()

        components = self._fields.get("components", [])

        if len(components) < 1 or len(components) > 5:
            raise ValueError("Количество компонентов в модальном окне должно быть больше 0 и меньше 5.")

        class ReturnModal(Modal):
            def __init__(self, fields: dict[str, Any]) -> None:
                super().__init__(
                    title=fields.get("title", str(uuid4()).split("-")[0]),
                    components=fields.get("components"),
                    custom_id=str(custom_id),
                    timeout=fields.get("timeout", 600)
                )
                self._fields = fields

            async def callback(self, interaction: ModalInteraction, /) -> Any:
                callback = self._fields.get("callback")

                if callback:
                    return await callback(interaction)

        return ReturnModal(fields=self._fields)
