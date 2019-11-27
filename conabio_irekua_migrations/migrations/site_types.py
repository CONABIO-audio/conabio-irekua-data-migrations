from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'licence_types'),
    ]

    items_subdir = 'types/sites'

    def load_models(self, apps):
        self.SiteType = apps.get_model('irekua_database', 'SiteType')

    def build_object(self, specification):
        schema_path = specification.pop('metadata_schema')
        specification['metadata_schema'] = self.load_schema(schema_path)
        self.SiteType.objects.get_or_create(**specification)
