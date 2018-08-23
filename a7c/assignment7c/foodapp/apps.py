# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class FoodappConfig(AppConfig):
    name = 'foodapp'

    def ready(self):
        import foodapp.signals  # noqa
