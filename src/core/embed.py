from disnake import Embed as Model, Guild


class Embed(Model):
    def __init__(self, *, title: str = None, description: str = None, color: int = 0x2b2d31, thumbnail_url: str = None, image_url: str = None, guild: Guild = None) -> None:
        super().__init__(
            title=title,
            description=description,
            color=color
        )

        if image_url:
            self.set_image(url=image_url)
        if thumbnail_url:
            self.set_thumbnail(url=thumbnail_url)

