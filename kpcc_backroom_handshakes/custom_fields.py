from django.db import models
from itertools import chain
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

class ListField(models.TextField):
    # __metaclass__ = models.SubfieldBase
    description = "Stores a python list"


    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        super(ListField, self).__init__(*args, **kwargs)


    def deconstruct(self):
        name, path, args, kwargs = super(ListField, self).deconstruct()
        # only include kwarg if it's not the default
        if self.separator != ",":
            kwargs['separator'] = self.separator
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        """
        displayed in the admin
        """
        if value is None:
            return value
        return value

    def to_python(self, value):
        """
        """
        if isinstance(value, list):
            return value
        if value is None:
            return value
        return "to_python"

    def get_prep_value(self, value):
        """
        saved to the database
        """
        return "saved to the database"


