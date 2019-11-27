import os
from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'mime_types'),
    ]

    items_subdir = 'types/devices'

    def load_models(self, apps):
        self.DeviceType = apps.get_model('irekua_database', 'DeviceType')
        self.MimeType = apps.get_model('irekua_database', 'MimeType')

    def build_object(self, specification):
        icon_path = specification.pop('icon', None)
        mime_types = specification.pop('mime_types', None)
        device_type, _ = self.DeviceType.objects.get_or_create(**specification)

        if icon_path is not None:
            self.add_icon(device_type, icon_path)

        if mime_types is not None:
            self.add_mime_types(device_type, mime_types)

    def add_icon(self, device_type, icon_path):
        image = self.load_image(icon_path)
        basename = os.path.basename(icon_path)
        device_type.icon.save(basename, image, save=True)
        image.close()

    def add_mime_types(self, device_type, mime_types):
        for mime_type in mime_types:
            mime_type = self.MimeType.objects.get(mime_type=mime_type)
            device_type.mime_types.add(mime_type)
        device_type.save()
