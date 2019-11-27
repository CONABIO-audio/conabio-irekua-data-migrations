from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'annotation_types'),
    ]

    items_subdir = 'types/mimes'

    def load_models(self, apps):
        self.MimeType = apps.get_model('irekua_database', 'MimeType')

    def build_object(self, specification):
        schema_path = specification['media_info_schema']
        specification['media_info_schema'] = self.load_schema(schema_path)
        self.MimeType.objects.get_or_create(**specification)
