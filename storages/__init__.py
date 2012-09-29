# -*- coding: utf-8 -*-
from storages.elliptics import Elliptics
import api_settings as settings


def create_storage():
    if settings.STORAGE == 'elliptics':
        return Elliptics()
