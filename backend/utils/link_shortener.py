import hashlib


class LinkShortener:
    """Класс для реализации метода сокращения ссылок, использующий hash."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.url_mapping = {}
        return cls._instance

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
