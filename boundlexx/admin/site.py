from copy import deepcopy

from django.contrib.admin.sites import AdminSite
from django.db.models.base import ModelBase


class BoundlexxAdminSite(AdminSite):
    def register(self, model_or_iterable, admin_class=None, **options):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]

        to_register = []
        for model in model_or_iterable:
            if hasattr(model, "admin_app_label"):
                model_copy = deepcopy(model)
                model_copy._meta.app_label = model.admin_app_label
                to_register.append(model_copy)
            else:
                to_register.append(model)

        return super().register(to_register, admin_class, **options)
