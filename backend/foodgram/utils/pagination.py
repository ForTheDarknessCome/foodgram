from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """ Кастомный класс пагинации с выдачей в 6 экземпляров """
    default_limit = 6
