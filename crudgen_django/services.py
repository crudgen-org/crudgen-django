import pathlib

from django.core.management import ManagementUtility
from crudgen.abstracts.services import BaseSimpleRestService

from .apps import App


class SimpleRestService(BaseSimpleRestService):
    _app_choices = {
        "default": App
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_base_dir: pathlib.Path = None
        self.dist_path: pathlib.Path = None
        self.default_settings_path: pathlib.Path = None
        self.settings_path: pathlib.Path = None
        self.settings_init_path: pathlib.Path = None
        self.base_urls_path: pathlib.Path = None

    def init_settings(self):
        # TODO: env package at 2020-10-24 by pooria
        settings_dir = self.project_base_dir / self.name / 'settings'
        settings_dir.mkdir(exist_ok=True)
        default_settings_path = self.project_base_dir / self.name / 'settings.py'
        if default_settings_path.exists():
            self.default_settings_path = default_settings_path.rename(settings_dir / 'defaults.py')

        self.settings_path = settings_dir / 'settings.py'

        self.settings_init_path = settings_dir / '__init__.py'

        with self.settings_path.open('w') as f:
            print('import pathlib', end='\n\n', file=f)
            print('from .defaults import *', end='\n\n', file=f)
            print('BASE_DIR = str(pathlib.Path(__file__).resolve().parents[2])', end='\n\n', file=f)
            print('INSTALLED_APPS += [', file=f)
            for app in self.apps:
                print(f"    '{app.name}',", end='\n', file=f)
            print("    'rest_framework',\n]", end='\n\n', file=f)

            print(f'ALLOWED_HOSTS = {repr(self.deploy_strategy["hostname"])}', file=f)

        with self.settings_init_path.open('w') as f:
            print('from .settings import *', end='\n\n\n', file=f)

    def create_base(self, dist_path):
        self.dist_path = pathlib.Path(dist_path).resolve()
        self.project_base_dir = self.dist_path
        self.dist_path.mkdir(parents=True, exist_ok=True)

    def generate_apps(self):
        self.base_urls_path = self.project_base_dir / self.name / 'urls.py'
        with self.base_urls_path.open('w') as f:
            print('from django.urls import path, include', end='\n\n', file=f)
            print('urlpatterns = [', end='\n', file=f)
            for app in self.apps:
                print(f"    path('{app.namespace}', include('{app.name}.urls')),", end='\n', file=f)
            print(']', end='\n\n', file=f)

    def generate_provision(self):
        vagrantfile = self.project_base_dir / 'Vagrantfile'
        bootstrapfile = self.project_base_dir / 'bootstrap.sh'
        requirementsfile = self.project_base_dir / 'requirements.txt'
        with vagrantfile.open('w') as f:
            print("# -*- mode: ruby -*-",
                  "# vi: set ft=ruby :",
                  "",
                  "Vagrant.configure(\"2\") do |config|",
                  "  config.vm.box = \"ubuntu/bionic64\"",
                  "  config.vm.provision :shell, path: \"bootstrap.sh\"",
                  "  # config.vm.network \"private_network\", ip: \"192.168.33.10\"",
                  "end", sep='\n', file=f)
        with bootstrapfile.open('w') as f:
            print("#!/usr/bin/env bash",
                  "",
                  "apt update",
                  "apt install -y python3 python3-pip virtualenv",
                  "",
                  "cd /vagrant",
                  "virtualenv -p python3 ./env",
                  "source ./env/bin/activate",
                  "pip install -r ./requirements.txt",
                  *[f"python manage.py makemigrations {app.name}" for app in self.apps],
                  *[f"python manage.py migrate {app.name}" for app in self.apps],
                  f"ufw allow {self.deploy_strategy['port']}",
                  f"nohup python manage.py runserver 0.0.0.0:{self.deploy_strategy['port']} &",
                  sep='\n', file=f)
        with requirementsfile.open('w') as f:
            print("Django<3.0",
                  "djangorestframework==3.12.1",
                  "drf-extensions==0.6.0",
                  "pytz==2020.1",
                  "sqlparse==0.4.1",
                  sep='\n', file=f
                  )

    def transform(self, dist_path, **kwargs):
        self.create_base(dist_path=dist_path)
        if not (self.dist_path / 'manage.py').exists():
            utility = ManagementUtility(['django-admin', 'startproject', self.name, str(self.dist_path)])
            utility.execute()

        self.init_settings()

        for app in self.apps:
            app.transform(self.project_base_dir)

        self.generate_apps()

        self.generate_provision()
