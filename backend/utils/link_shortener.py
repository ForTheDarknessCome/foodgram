import hashlib


class LinkShortener:
    """Класс для реализации метода сокращения ссылок, использующий hash."""

    def __init__(self) -> None:
        self.url_mapping: dict[str, str] = {}

    def shorten_url(self, full_url: str) -> str:
        """Создание короткого URL на основе хеширования полного URL."""
        short_key = hashlib.md5(full_url.encode()).hexdigest()[:3]
        short_url = f's/{short_key}'
        self.url_mapping[short_url] = full_url
        return short_url

    def restore_url(self, short_url: str) -> str:
        """Восстанавливает полный URL на основе короткого URL.

        Возвращает сообщение, если URL не найден.
        """
        return self.url_mapping.get(short_url, 'URL не найден')
