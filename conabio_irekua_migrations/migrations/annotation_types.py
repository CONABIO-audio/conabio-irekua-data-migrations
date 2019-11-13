from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'catalogos_taxonomicos_conabio'),
    ]

    types_subdir = 'annotations'

    def load_models(self, apps):
        self.AnnotationType = apps.get_model('irekua_database', 'AnnotationType')

    def build_object(self, specification):
        schema_path = specification['annotation_schema']
        specification['annotation_schema'] = self.load_schema(schema_path)
        self.AnnotationType.objects.get_or_create(**specification)
