import hashlib
from cooking.models import ShortenedURL


class LinkShortener:
    """Класс для реализации метода сокращения ссылок, использующий hash."""

    def shorten_url(self, full_url: str) -> str:
        """Создание короткого URL на основе хеширования полного URL."""
        short_key = hashlib.md5(full_url.encode()).hexdigest()[:6]
        short_link, _ = ShortenedURL.objects.get_or_create(
            full_url=full_url, defaults={'short_key': short_key}
        )
        return short_link.short_key

    def restore_url(self, short_key: str) -> str:
        try:
            return ShortenedURL.objects.get(short_key=short_key).full_url
        except ShortenedURL.DoesNotExist:
            return 'URL не найден'
