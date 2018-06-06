import binascii
import os
from inspect import isclass


def generate_string(length=20):
    return binascii.hexlify(os.urandom(length)).decode()


def get_class(obj):
    return obj if isclass(obj) else obj.__class__


def get_object(cls):
    return cls() if isclass(cls) else cls
