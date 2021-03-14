from crudgen.abstracts.endpoints import SimpleDataAccessEndpoint, NestedManySimpleDataAccessEndpoint, \
    BaseAddToManyRelationEndpoint, BaseRemoveFromManyRelationEndpoint, NestedForeignSimpleDataAccessEndpoint


class NestedManyModelViewSetEndpoint(NestedManySimpleDataAccessEndpoint):

    template = "class {name}(NestedViewSetMixin, viewsets.ModelViewSet):\n" \
               "    serializer_class = {serializer}\n" \
               "    queryset = {model}.objects.all()\n" \
               "\n" \
               "    def perform_create(self, serializer):\n" \
               "        obj = serializer.save()\n" \
               "        obj.{parent_field}.add(self.kwargs['parent_lookup_{parent_field}'])"

    @property
    def name(self):
        return f"{self.parent.model.name}{self.model.name}{self.serializer.name}ViewSet"

    @property
    def code(self):
        return self.__class__.template.format(
            name=self.name, serializer=self.serializer.name, model=self.model.name,
            parent_field=self.parent_field.name
        )


class CustomActionMixin:
    pass


class AddToManyRelation(BaseAddToManyRelationEndpoint, CustomActionMixin):

    template = "    @action(detail=True, url_path='{path}', methods=['put'])\n" \
               "    def {name}(self, request, pk=None):\n" \
               "        obj = self.get_object()\n" \
               "        obj.{parent_field}.add(request.data['id'])\n" \
               "        return Response(status=status.HTTP_200_OK, data={{'status': 'success'}})\n"

    @property
    def name(self):
        return f"{self.parent.model.name.lower()}_add_{self.model.name.lower()}"

    @property
    def code(self):
        return self.__class__.template.format(
            path=self.path, name=self.name, parent_field=self.parent_field.name
        )


class RemoveFromManyRelation(BaseRemoveFromManyRelationEndpoint, CustomActionMixin):

    template = "    @action(detail=True, url_path='{path}', methods=['put'])\n" \
               "    def {name}(self, request, pk=None):\n" \
               "        obj = self.get_object()\n" \
               "        obj.{parent_field}.remove(request.data['id'])\n" \
               "        return Response(status=status.HTTP_200_OK, data={{'status': 'success'}})\n"

    @property
    def name(self):
        return f"{self.parent.model.name.lower()}_remove_{self.model.name.lower()}"

    @property
    def code(self):
        return self.__class__.template.format(
            path=self.path, name=self.name, parent_field=self.parent_field.name
        )


class NestedForeignModelViewSet(NestedForeignSimpleDataAccessEndpoint, NestedManyModelViewSetEndpoint):
    template = "class {name}(NestedViewSetMixin, viewsets.ModelViewSet):\n" \
               "    serializer_class = {serializer}\n" \
               "    queryset = {model}.objects.all()\n" \
               "\n" \
               "    def perform_create(self, serializer):\n" \
               "        obj = serializer.save({parent_field}_id=self.kwargs['parent_lookup_{parent_field}'])\n"


class ModelViewSetEndpoint(SimpleDataAccessEndpoint):

    nested_endpoints = {
        "nested_many_simple_data_access": NestedManyModelViewSetEndpoint,
        "add_relation": AddToManyRelation,
        "remove_relation": RemoveFromManyRelation,
        "nested_foreign_simple_data_access": NestedForeignModelViewSet
    }

    template = "class {name}(viewsets.ModelViewSet):\n" \
               "    serializer_class = {serializer}\n" \
               "    queryset = {model}.objects.all()\n"

    @property
    def name(self):
        return f"{self.model.name}{self.serializer.name}ViewSet"

    @property
    def code(self):
        definition = self.__class__.template.format(
            name=self.name, serializer=self.serializer.name, model=self.model.name
        )
        for action in filter(lambda ac: isinstance(ac, CustomActionMixin), self.actions):
            definition += f"\n{action.code}"

        return definition
