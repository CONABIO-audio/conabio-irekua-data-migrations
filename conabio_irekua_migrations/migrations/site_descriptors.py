from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'site_descriptor_types'),
    ]

    items_subdir = 'site_descriptors'

    def load_models(self, apps):
        self.SiteDescriptor = apps.get_model('irekua_database', 'SiteDescriptor')
        self.SiteDescriptorType = apps.get_model('irekua_database', 'SiteDescriptorType')

    def build_object(self, specification):
        site_descriptor_type = specification.pop('descriptor_type')
        site_descriptor_type = self.SiteDescriptorType.objects.get(name=site_descriptor_type)

        specification['descriptor_type'] = site_descriptor_type
        self.SiteDescriptor.objects.get_or_create(**specification)
