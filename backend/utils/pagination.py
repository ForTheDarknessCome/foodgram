from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """Кастомный класс пагинации с выдачей в 6 экземпляров."""

    page_size_query_param = 'limit'
