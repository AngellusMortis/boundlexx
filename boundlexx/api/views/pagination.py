from rest_framework.pagination import LimitOffsetPagination


class TimeseriesPagination(LimitOffsetPagination):
    page_size = 50


class WorldPollPagination(LimitOffsetPagination):
    page_size = 10
