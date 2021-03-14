from crudgen.abstracts.serializers import BaseSerializer

from .fields import *


class ModelSerializer(BaseSerializer):

    def get_serialized_field(self, field_name, options):
        # TODO: handle source specified at 2020-10-27 by pooria
        model_field_name = options.get('source') or field_name
        field = self.model.get_field(model_field_name)
        if isinstance(field, (RelatedField, ManyToMany)):
            if options.get('source'):
                return " " * 8 + f"self.fields['{field_name}'] = {options['serializer']}(many=True, read_only=True" \
                                 f", source='{options['source']}')\n"
            else:
                return " "*8 + f"self.fields['{field_name}'] = {options['serializer']}(many=True, read_only=True)\n"
        else:
            if options.get('source'):
                return " " * 8 + f"self.fields['{field_name}'] = {options['serializer']}(read_only=True" \
                                 f", source='{options['source']}')\n"
            else:
                return " "*8 + f"self.fields['{field_name}'] = {options['serializer']}(read_only=True)\n"

    @property
    def code(self):
        definiation = f"class {self.name}(serializers.ModelSerializer):\n\n"
        init = "    def __init__(self, *args, **kwargs):\n" + \
               "        super().__init__(*args, **kwargs)\n"
        meta_fields = self.field_names[:]
        for key, val in self.extras.items():
            if val.get('serializer'):
                meta_fields.remove(key)
                init += self.get_serialized_field(key, val)
        init += '\n'

        meta = f"    class Meta:\n" + \
               f"        model = {self.model.name}\n" + \
               "        fields = [{fields}]".format(
                   fields=", ".join(f"'{field}'" for field in meta_fields)
               )
        other_extra_kwargs = {}
        for field_name, options in self.extras.items():
            serialized = options.get('serializer', None)
            if serialized is None:
                other_extra_kwargs[field_name] = options

        if other_extra_kwargs:
            meta += f"\n        extra_kwargs = {other_extra_kwargs}"
        return definiation + init + meta
