import hashlib


class LinkShortener:
    """Класс для реализации метода сокращения ссылок, использующий hash."""

    def __init__(self) -> None:
        self.url_mapping: dict[str, str] = {}

    def shorten_url(self, full_url: str) -> str:
        """Создание короткого URL на основе хеширования полного URL."""
        short_key = hashlib.md5(full_url.encode()).hexdigest()[:6]
        self.url_mapping[short_key] = full_url
        return short_key

    def restore_url(self, short_key: str) -> str:
        """Восстанавливает полный URL на основе короткого URL.

        Возвращает сообщение, если URL не найден.
        """
        return self.url_mapping.get(short_key, 'URL не найден')
