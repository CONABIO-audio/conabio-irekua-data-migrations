from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'site_types'),
    ]

    items_subdir = 'types/sampling_events'

    def load_models(self, apps):
        self.SamplingEventType = apps.get_model('irekua_database', 'SamplingEventType')
        self.DeviceType = apps.get_model('irekua_database', 'DeviceType')
        self.SiteType = apps.get_model('irekua_database', 'SiteType')
        self.SamplingEventTypeDeviceType = apps.get_model(
            'irekua_database', 'SamplingEventTypeDeviceType')

    def build_object(self, specification):
        device_types = specification.pop('device_types', None)
        site_types = specification.pop('site_types', None)

        schema_path = specification.pop('metadata_schema')
        specification['metadata_schema'] = self.load_schema(schema_path)
        sampling_event_type, _ = self.SamplingEventType.objects.get_or_create(
            **specification)

        if device_types is not None and sampling_event_type.restrict_device_types:
            self.add_device_types(sampling_event_type, device_types)

        if site_types is not None and sampling_event_type.restrict_site_types:
            self.add_site_types(sampling_event_type, site_types)

    def add_device_types(self, sampling_event_type, device_types):
        for device_type in device_types:
            name = device_type['name']
            metadata_schema = self.load_schema(device_type['metadata_schema'])
            device_type = self.DeviceType.objects.get(name=name)

            self.SamplingEventTypeDeviceType.objects.create(
                sampling_event_type=sampling_event_type,
                device_type=device_type,
                metadata_schema=metadata_schema)
        sampling_event_type.save()

    def add_site_types(self, sampling_event_type, site_types):
        for site_type in site_types:
            site_type = self.SiteType.objects.get(name=site_type)
            sampling_event_type.site_types.add(site_type)
        sampling_event_type.save()
