from crudgen.abstracts.abc import AbstractBaseField
from crudgen.abstracts.fields import BaseCharField, BaseForeignKey, BaseRelatedField, BaseManyToMany, BaseBooleanField


class AutoIDField(AbstractBaseField):

    @property
    def code(self):
        pass

    @classmethod
    def from_dict(cls, data: dict):
        pass


class BooleanField(BaseBooleanField):

    @property
    def code(self):
        return f"{self.name} = models.BooleanField(default=False)"


class CharField(BaseCharField):

    @property
    def code(self):
        return f"{self.name} = models.CharField(max_length={self.max_length})"


class ForeignKey(BaseForeignKey):

    @property
    def code(self):
        # TODO: on delete at 2020-10-27 by pooria
        # TODO: do something about null=True at 2020-10-29 by pooria
        return f"{self.name} = models.ForeignKey('{self.target}', null=True, on_delete=models.CASCADE, related_name='{self.related_name}', related_query_name='{self.related_query_name}')"


class ManyToMany(BaseManyToMany):

    @property
    def code(self):
        return f"{self.name} = models.ManyToManyField('{self.target}', related_name='{self.related_name}', related_query_name='{self.related_query_name}')"


class RelatedField(BaseRelatedField):

    @classmethod
    def from_dict(cls, data: dict):
        pass

    @property
    def code(self):
        return None

