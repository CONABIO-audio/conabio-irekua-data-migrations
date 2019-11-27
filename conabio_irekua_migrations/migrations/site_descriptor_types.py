from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'marco_geoestadistico'),
    ]

    items_subdir = 'types/site_descriptors'

    def load_models(self, apps):
        self.SiteDescriptorType = apps.get_model('irekua_database', 'SiteDescriptorType')

    def build_object(self, specification):
        schema_path = specification.pop('metadata_schema', None)
        if schema_path:
            specification['metadata_schema'] = self.load_schema(schema_path)

        self.SiteDescriptorType.objects.get_or_create(**specification)
