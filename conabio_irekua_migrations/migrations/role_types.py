from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'event_types'),
    ]

    items_subdir = 'types/roles'

    def load_models(self, apps):
        self.Role = apps.get_model('irekua_database', 'Role')
        self.Permission = apps.get_model('auth', 'Permission')

    def build_object(self, specification):
        permissions = specification.pop('permissions', None)
        role, _ = self.Role.objects.get_or_create(**specification)

        if permissions is not None:
            self.add_permissions(role, permissions)

    def add_permissions(self, role, permissions):
        for permission in permissions:
            permission = self.Permission.objects.get(codename=permission)
            role.permissions.add(permission)
        role.save()
