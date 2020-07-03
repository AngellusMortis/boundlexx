from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    gui_name = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return self.gui_name
