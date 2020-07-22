"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'app.menu.CustomMenu'
"""

from admin_tools.menu import Menu, items
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from bge.admin import ADMIN_APPS


class BGEMenu(Menu):
    """
    Custom Menu for app admin site.
    """

    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_("BGE"), reverse("admin:index")),
            items.Bookmarks(),
            items.AppList(_("Data"), exclude=ADMIN_APPS),
            items.AppList(_("Administration"), models=ADMIN_APPS),
        ]
