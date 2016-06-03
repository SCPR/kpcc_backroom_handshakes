from django.db import models
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

class ListField(models.TextField):
    # __metaclass__ = models.SubfieldBase
    description = "Stores a python list"


    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(ListField, self).__init__(*args, **kwargs)


    # def deconstruct(self):
    #     name, path, args, kwargs = super(ListField, self).deconstruct()
    #     # only include kwarg if it's not the default
    #     if self.token != ",":
    #         kwargs['separator'] = self.separator
    #     return name, path, args, kwargs


    def to_python(self, value):
        if not value:
            return
        if isinstance(value, list):
            return value
        return value.split(self.token)


    # def from_db_value(self, value, expression, connection, context):
    #     if value is None:
    #         return value
    #     return value.split(self.token)


    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])


    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
