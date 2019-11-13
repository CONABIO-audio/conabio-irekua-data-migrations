import os
from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'item_types'),
    ]

    types_subdir = 'collections'

    def load_models(self, apps):
        self.CollectionType = apps.get_model('irekua_database', 'CollectionType')
        self.SiteType = apps.get_model('irekua_database', 'SiteType')
        self.AnnotationType = apps.get_model('irekua_database', 'AnnotationType')
        self.ItemType = apps.get_model('irekua_database', 'ItemType')
        self.CollectionItemType = apps.get_model('irekua_database', 'CollectionItemType')
        self.LicenceType = apps.get_model('irekua_database', 'LicenceType')
        self.DeviceType = apps.get_model('irekua_database', 'DeviceType')
        self.CollectionDeviceType = apps.get_model('irekua_database', 'CollectionDeviceType')
        self.EventType = apps.get_model('irekua_database', 'EventType')
        self.SamplingEventType = apps.get_model('irekua_database', 'SamplingEventType')
        self.Role = apps.get_model('irekua_database', 'Role')
        self.CollectionRole = apps.get_model('irekua_database', 'CollectionRole')

    def build_object(self, specification):
        schema_path = specification.pop('metadata_schema')
        specification['metadata_schema'] = self.load_schema(schema_path)

        logo_path = specification.pop('logo', None)
        site_types = specification.pop('site_types', None)
        annotation_types = specification.pop('annotation_types', None)
        item_types = specification.pop('item_types', None)
        licence_types = specification.pop('licence_types', None)
        device_types = specification.pop('device_types', None)
        event_types = specification.pop('event_types', None)
        sampling_event_types = specification.pop('sampling_event_types', None)
        roles = specification.pop('roles', None)

        collection_type, _ = self.CollectionType.objects.get_or_create(**specification)

        if logo_path is not None:
            self.add_logo(collection_type, logo_path)

        if site_types is not None and collection_type.restrict_site_types:
            self.add_site_types(collection_type, site_types)

        if annotation_types is not None and collection_type.restrict_annotation_types:
            self.add_annotation_types(collection_type, annotation_types)

        if item_types is not None and collection_type.restrict_item_types:
            self.add_item_types(collection_type, item_types)

        if licence_types is not None and collection_type.restrict_licence_types:
            self.add_licence_types(collection_type, licence_types)

        if device_types is not None and collection_type.restrict_device_types:
            self.add_device_types(collection_type, device_types)

        if event_types is not None and collection_type.restrict_event_types:
            self.add_event_types(collection_type, event_types)

        if sampling_event_types is not None and collection_type.restrict_sampling_event_types:
            self.add_sampling_event_types(collection_type, sampling_event_types)

        if roles is not None:
            self.add_roles(collection_type, roles)

    def add_logo(self, collection_type, logo_path):
        image = self.load_image(logo_path)
        basename = os.path.basename(logo_path)
        collection_type.icon.save(basename, image, save=True)
        image.close()

    def add_site_types(self, collection_type, site_types):
        for site_type in site_types:
            site_type = self.SiteType.objects.get(name=site_type)
            collection_type.site_types.add(site_type)
        collection_type.save()

    def add_annotation_types(self, collection_type, annotation_types):
        for annotation_type in annotation_types:
            annotation_type = self.AnnotationType.objects.get(name=annotation_type)
            collection_type.annotation_types.add(annotation_type)
        collection_type.save()

    def add_item_types(self, collection_type, item_types):
        for item_type in item_types:
            metadata_schema = self.load_schema(item_type['metadata_schema'])
            item_type = self.ItemType.objects.get(name=item_type['name'])
            self.CollectionItemType.objects.create(
                collection_type=collection_type,
                item_type=item_type,
                metadata_schema=metadata_schema)
        collection_type.save()

    def add_licence_types(self, collection_type, licence_types):
        for licence_type in licence_types:
            licence_type = self.LicenceType.objects.get(name=licence_type)
            collection_type.licence_types.add(licence_type)
        collection_type.save()

    def add_device_types(self, collection_type, device_types):
        for device_type in device_types:
            metadata_schema = self.load_schema(device_type['metadata_schema'])
            device_type = self.DeviceType.objects.get(name=device_type['name'])
            self.CollectionDeviceType.objects.create(
                collection_type=collection_type,
                device_type=device_type,
                metadata_schema=metadata_schema)
        collection_type.save()

    def add_event_types(self, collection_type, event_types):
        for event_type in event_types:
            event_type = self.EventType.objects.get(name=event_type)
            collection_type.event_types.add(event_type)
        collection_type.save()

    def add_sampling_event_types(self, collection_type, sampling_event_types):
        for sampling_event_type in sampling_event_types:
            sampling_event_type = self.SamplingEventType.objects.get(name=sampling_event_type)
            collection_type.sampling_event_types.add(sampling_event_type)
        collection_type.save()

    def add_roles(self, collection_type, roles):
        for role in roles:
            metadata_schema = self.load_schema(role['metadata_schema'])
            role = self.Role.objects.get(name=role['name'])
            self.CollectionRole.objects.create(
                collection_type=collection_type,
                role=role,
                metadata_schema=metadata_schema)
        collection_type.save()
