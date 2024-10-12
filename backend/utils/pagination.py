from rest_framework.pagination import PageNumberPagination

from utils.constants import PAGE_SIZE


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомный класс пагинации с выдачей в 6 экземпляров."""

    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = PAGE_SIZE
