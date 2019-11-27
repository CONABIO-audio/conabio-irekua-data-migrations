import os
from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'role_types'),
    ]

    items_subdir = 'types/licences'

    def load_models(self, apps):
        self.LicenceType = apps.get_model('irekua_database', 'LicenceType')

    def build_object(self, specification):
        metadata_schema_path = specification.pop('metadata_schema')
        document_template = specification.pop('document_template', None)
        icon_path = specification.pop('icon', None)

        specification['metadata_schema'] = self.load_schema(metadata_schema_path)

        licence, _ = self.LicenceType.objects.get_or_create(**specification)

        if document_template is not None:
            self.add_document_template(licence, document_template)

        if icon_path is not None:
            self.add_icon(licence, icon_path)

    def add_document_template(self, licence, document_template):
        image = self.load_licence_template(document_template)
        basename = os.path.basename(document_template)
        licence.document_template.save(basename, image, save=True)
        image.close()

    def add_icon(self, licence, icon_path):
        image = self.load_image(icon_path)
        basename = os.path.basename(icon_path)
        licence.icon.save(basename, image, save=True)
        image.close()
