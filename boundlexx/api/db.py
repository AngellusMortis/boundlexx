from django.db.models.aggregates import Aggregate
from django.db.models.functions.mixins import (
    FixDurationInputMixin,
    NumericOutputFieldMixin,
)


class Mode(
    FixDurationInputMixin, NumericOutputFieldMixin, Aggregate
):  # pylint: disable=abstract-method
    template = "%(function)s() WITHIN GROUP (ORDER BY %(expressions)s)"
    function = "mode"
    name = "Mode"
    allow_distinct = False


class Median(
    FixDurationInputMixin, NumericOutputFieldMixin, Aggregate
):  # pylint: disable=abstract-method
    function = "median"
    name = "Median"
    allow_distinct = False
