from abc import abstractmethod
import glob
import os
import json

from django.core.files import File
from django.db import migrations
import yaml

from conabio_irekua_migrations import APP_DIRECTORY
from conabio_irekua_migrations import ITEMS_DIR
from conabio_irekua_migrations import IMAGES_DIR
from conabio_irekua_migrations import SCHEMA_DIR
from conabio_irekua_migrations import LICENCE_TEMPLATES_DIR


class BaseMigration(migrations.Migration):
    items_subdir = None

    def __init__(self, name, app_label):
        super().__init__(name, app_label)
        self.operations = [
            migrations.RunPython(self.migrate)
        ]

    def migrate(self, apps, schema_editor):
        self.load_models(apps)

        files = self.load_files()
        for filename in files:
            self.add_object_from_file(filename)

    def load_files(self):
        return glob.glob(os.path.join(
            APP_DIRECTORY,
            ITEMS_DIR,
            self.items_subdir,
            '*.yaml'
        ))

    def add_object_from_file(self, filename):
        specification = self.load_specification(filename)
        self.build_object(specification)

    def load_specification(self, filename):
        with open(filename, 'r') as yaml_file:
            specification = yaml.full_load(yaml_file)
        return specification

    def load_image(self, image_path):
        full_image_path = os.path.join(
            APP_DIRECTORY,
            IMAGES_DIR,
            image_path)
        image = File(open(full_image_path, 'rb'))
        return image

    def load_licence_template(self, template_path):
        full_image_path = os.path.join(
            APP_DIRECTORY,
            LICENCE_TEMPLATES_DIR,
            template_path)
        template = File(open(full_image_path, 'rb'))
        return template

    def load_schema(self, schema_path):
        full_schema_path = os.path.join(
            APP_DIRECTORY,
            SCHEMA_DIR,
            schema_path)
        with open(full_schema_path, 'r') as json_file:
            schema = json.load(json_file)
        return schema

    @abstractmethod
    def load_models(self, apps):
        pass

    @abstractmethod
    def build_object(self, specification):
        pass
