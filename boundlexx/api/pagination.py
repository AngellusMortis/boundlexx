from rest_framework.pagination import LimitOffsetPagination


class MaxLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 1000
