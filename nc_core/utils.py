import datetime
import logging

import sqlparse
from django.core import validators
from django.core.cache import caches
from django.db import models
from django_redis import get_redis_connection

__all__ = (
    'memcached_method',
    'memcached_property',
    'SqlParseFormatter',
    'FIELD_TYPE_MAP',
    'FieldRegex',
    'get_field_type'
)


def memcached_method(key, timeout, cache=None):
    """
    Uses django cache to store value.
    Use `class_or_instance.function.clear_cache(*args, **kwargs)` to delete cached value
    """
    cache = cache or caches['default']

    def decorator(fn):
        fn_name = fn.__name__

        def get_key(*args, **kwargs):
            return (key(*args, **kwargs) if callable(key) else key) + "(method)" + fn_name

        def clear_cache(*args, **kwargs):
            cache.delete(get_key(*args, **kwargs))

        def wrapper(self, *args, **kwargs):
            cache_key = get_key(*args, **kwargs)
            cache_item = cache.get(cache_key)
            if cache_item is None:
                cache_item = fn(self, *args, **kwargs)
                cache.set(cache_key, cache_item, timeout)
            return cache_item

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator


def memcached_property(key, timeout, cache=None):
    """Uses django cache to store value. Use Class.property_name.fget.clear_cache(instance) to delete cached value"""
    cache = cache or caches['default']

    def decorator(fn):
        fn_name = fn.__name__

        def get_key(self):
            return (key(self) if callable(key) else key) + "(prop)" + fn_name

        def clear_cache(self):
            cache.delete(get_key(self))

        def wrapper(self):
            cache_key = get_key(self)
            cache_item = cache.get(cache_key)
            if cache_item is None:
                cache_item = fn(self)
                cache.set(cache_key, cache_item, timeout)
            return cache_item

        wrapper.clear_cache = clear_cache
        return property(wrapper)

    return decorator


class SqlParseFormatter(logging.Formatter):
    """Format sql log to human-friendly format"""
    def format(self, record):
        return "--{time} {duration}\n{sql};\n".format(
            time=datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S"),
            duration=(record.duration * 1000) if hasattr(record, 'duration') else 0,
            sql=sqlparse.format(record.sql, reindent=True, keyword_case='upper')
        )


FIELD_TYPE_MAP = {
    models.IntegerField: "int",
    models.FloatField: "float",
    models.CharField: "str",
    models.TextField: "str",
    models.DateField: "date",
    models.DateTimeField: "datetime",
    models.DecimalField: "str"
}


def get_field_type(field: models.Field):
    for cls in FIELD_TYPE_MAP.keys():
        if isinstance(field, cls):
            return FIELD_TYPE_MAP[cls]
    else:
        return None


def wrap(regex: str) -> str:
    return "(?:" + regex + ")"


class FieldRegex:
    """
    Get a regular expression from model's field instance

    Float field & DateTime field are not implemented yet
    """
    def __init__(self, field: models.Field):
        self.field = field
        self.blank = field.blank
        self.choices = [name for name, verb in field.flatchoices]
        self.max_length = field.max_length or getattr(field, "max_digits", 0) or 1000

    @property
    def prefix(self):
        if isinstance(self.field, models.IntegerField) and not isinstance(self.field, models.PositiveIntegerField):
            return wrap(r"\+|\-|")
        return ""

    @property
    def charset(self):
        if isinstance(self.field, models.IntegerField) or isinstance(self.field, models.DecimalField):
            return "[0-9]"
        return "."

    @property
    def regex(self):
        if isinstance(self.field, models.FloatField):
            return ".+"
        elif isinstance(self.field, models.DateField):
            base = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
            if self.blank:
                base = wrap(base) + "?"
            return base

        field_validators = self.field.validators
        if field_validators:
            for validator in field_validators:
                if isinstance(validator, validators.RegexValidator):
                    return validator.regex

        if self.choices:
            base = wrap("|".join(self.choices)) + ("?" if self.blank else "")
        else:
            base = self.prefix + self.charset + "{1,%i}" % self.max_length
            if self.blank:
                base = wrap(base) + "?"

        return "^" + base + "$"


class RedisLogHandler(logging.Handler):
    """
    Publish exceptions tracebacks to redis `log-channel`
    """
    try:
        redis = get_redis_connection('default')
    except NotImplementedError:
        redis = None

    def format(self, record):
        """
        Just a little bit of reformatting for better readability
        """
        msg = super().format(record)
        lines = msg.split("\n")
        out_lines = []
        _flag = False
        for line in map(str.strip, lines):
            if _flag:
                line = ">>> " + line
            if line.startswith("File"):
                out_lines.append(" ")
                _flag = True
            else:
                _flag = False
            out_lines.append(line)

        return "\n".join(out_lines)

    def emit(self, record):
        if self.redis:
            self.redis.publish("log-channel", self.format(record))
