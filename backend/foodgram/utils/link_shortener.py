import hashlib


class LinkShortener:
    def __init__(self):
        self.url_mapping = {}

    def shorten_url(self, full_url):
        short_key = hashlib.md5(full_url.encode()).hexdigest()[:3]
        short_url = f"s/{short_key}"
        self.url_mapping[short_url] = full_url
        return short_url

    def restore_url(self, short_url):
        return self.url_mapping.get(short_url, "URL не найден")
