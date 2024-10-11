from rest_framework.pagination import LimitOffsetPagination

from utils.constants import DEFAULT_PAGINATION_LIMIT, PAGE_SIZE


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """Кастомный класс пагинации с выдачей в 6 экземпляров."""

    default_limit = DEFAULT_PAGINATION_LIMIT
    page_size = PAGE_SIZE
