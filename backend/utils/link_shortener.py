import hashlib
from cooking.models import ShortenedURL


class LinkShortener:
    """Класс для реализации метода сокращения ссылок, использующий hash."""

    def shorten_url(self, full_url: str) -> str:
        """Создание короткого URL на основе хеширования полного URL."""
        short_key = hashlib.md5(full_url.encode()).hexdigest()[:6]
        ShortenedURL.objects.create(full_url=full_url, short_key=short_key)
        return short_key

    def restore_url(self, short_key: str) -> str:
        url_entry = (
            ShortenedURL.objects.filter(short_key=short_key)
            .values('full_url')
            .first()
        )
        if url_entry:
            return url_entry['full_url']
        return 'URL не найден'
