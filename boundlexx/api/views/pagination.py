from rest_framework.pagination import LimitOffsetPagination


class TimeseriesPagination(LimitOffsetPagination):
    default_limit = 50
