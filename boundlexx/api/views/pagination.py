from rest_framework.pagination import LimitOffsetPagination


class TimeseriesPagination(LimitOffsetPagination):
    default_limit = 50


class WorldPollPagination(LimitOffsetPagination):
    default_limit = 10
