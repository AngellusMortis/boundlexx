from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=64)
    gui_name = models.CharField(max_length=64)

    def __str__(self):
        return self.gui_name
