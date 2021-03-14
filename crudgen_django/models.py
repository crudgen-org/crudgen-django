from crudgen.abstracts.models import DBModel

from .fields import CharField, ForeignKey, AutoIDField, RelatedField, ManyToMany, BooleanField
from .serializers import ModelSerializer


class Model(DBModel):

    _field_choices = {
        "CharField": CharField,
        "ForeignKey": ForeignKey,
        "related_field": RelatedField,
        "ManyToMany": ManyToMany,
        "BooleanField": BooleanField
    }

    _serializer_choices = {
        "default": ModelSerializer
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: create the id field only if there is no pk at 2020-10-27 by pooria
        self.register_field(AutoIDField(name='id', field_type='auto_id'))

    @property
    def code(self):
        # TODO: checkout template engines to do this properly at 2020-10-16 by pooria
        defination = f"class {self.name}(models.Model):\n"
        fields = "\n".join(f"    {field.code}" for field in filter(lambda x: not isinstance(x, (AutoIDField, RelatedField))
                                                                   , self.fields))
        return defination + fields
