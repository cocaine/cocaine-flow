# -*- coding: utf-8 -*-

class StorageException(Exception):
    pass

class UserExists(StorageException):
    pass
