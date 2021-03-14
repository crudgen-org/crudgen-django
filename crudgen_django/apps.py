import pathlib

from .models import Model
from .endpoints import ModelViewSetEndpoint
from crudgen.abstracts.apps import BaseApp


class App(BaseApp):
    _model_choices = {
        "default": Model,
        "DBModel": Model
    }

    _endpoint_choices = {
        "default": ModelViewSetEndpoint,
        "simple_data_access": ModelViewSetEndpoint
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_dir: str = None
        self.path: pathlib.Path = None
        self.models_path: pathlib.Path = None
        self.views_path: pathlib.Path = None
        self.urls_path: pathlib.Path = None
        self.serializers_path: pathlib.Path = None

    def create_structure(self, base_dir):
        self.base_dir = base_dir
        if isinstance(base_dir, pathlib.Path):
            self.path = base_dir / self.name
        else:
            self.path = pathlib.Path(base_dir) / self.name
        self.path.mkdir(parents=True, exist_ok=True)
        self.models_path = self.path / "models.py"
        self.views_path = self.path / "views.py"
        self.urls_path = self.path / "urls.py"
        self.serializers_path = self.path / "serializers.py"

    def add_models_imports(self, file):
        print("from django.db import models", file=file, end='\n' * 3)

    def generate_models(self):
        with self.models_path.open('w') as f:
            self.add_models_imports(file=f)
            for model in self.models:
                print(model.code, file=f, end='\n'*3)

    def add_views_imports(self, file):
        print("from rest_framework import viewsets", file=file, end='\n')
        print("from rest_framework.decorators import action", file=file, end='\n')
        print("from rest_framework import status", file=file, end='\n')
        print("from rest_framework.response import Response", file=file, end='\n')
        print("from rest_framework_extensions.mixins import NestedViewSetMixin", file=file, end='\n'*2)
        model_imports = "from .models import (\n    {model_names}\n)".format(
            model_names=",\n    ".join(model.name for model in self.models)
        )
        serializers_imports = "from .serializers import *"
        print(model_imports, file=file, end='\n'*3)
        print(serializers_imports, file=file, end='\n'*3)

    def generate_views(self):
        with self.views_path.open('w') as f:
            self.add_views_imports(file=f)
            for endpoint in self.endpoints:
                print(endpoint.code, file=f, end='\n'*2)

    def add_urls_imports(self, file):
        print("from rest_framework_extensions.routers import ExtendedDefaultRouter", file=file)
        viewset_imports = "from .views import (\n    {viewset_names}\n)".format(
            viewset_names=",\n    ".join(endpoint.name for endpoint in self.endpoints)
        )
        print(viewset_imports, file=file, end='\n'*3)

    def generate_urls(self):
        with self.urls_path.open('w') as f:
            self.add_urls_imports(file=f)
            print("router = ExtendedDefaultRouter()", file=f, end='\n'*2)
            for endpoint in filter(lambda end: end.parent is None, self.endpoints):
                print(f"{endpoint.path}_router = router.register(r'{endpoint.path}', {endpoint.name})", file=f, end='\n')
            for endpoint in filter(lambda end: end.parent is not None, self.endpoints):
                print(f"{endpoint.parent.path}_{endpoint.path.replace('-', '_')}_router = {endpoint.parent.path}_router.register("
                      f"r'{endpoint.path}', {endpoint.name}, basename='{endpoint.parent.path}-{endpoint.path}', "
                      f"parents_query_lookups=['{endpoint.parent_field.name}'])", file=f, end='\n')
            print("urlpatterns = router.urls", file=f, end='\n')

    def add_serializers_imports(self, file):
        print("from rest_framework import serializers", file=file, end='\n' * 3)

        model_imports = "from .models import (\n    {model_names}\n)".format(
            model_names=",\n    ".join(model.name for model in self.models)
        )
        print(model_imports, file=file, end='\n' * 3)

        # TODO: import other apps serializers at 2020-10-27 by pooria

    def generate_serializers(self):
        with self.serializers_path.open('w') as f:
            self.add_serializers_imports(file=f)
            for model in self.models:
                for serializer in model.serializers:
                    print(serializer.code, file=f, end='\n' * 3)

    def transform(self, base_dir):
        # create associated files need for an app in django
        self.create_structure(base_dir=base_dir)
        # generates code in models.py based on models associated to this app
        self.generate_models()
        # generates code in views.py for all endpoints associated to this app
        self.generate_views()
        # generates url patterns in urls.py based on paths of each endpoint associated to this app
        self.generate_urls()
        # generates code in serializers.py based on serializers of each model associated to this app
        self.generate_serializers()
