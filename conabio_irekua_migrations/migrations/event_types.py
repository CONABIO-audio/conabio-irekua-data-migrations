import os
from conabio_irekua_migrations.base_migration import BaseMigration


class Migration(BaseMigration):
    dependencies = [
        ('conabio_irekua_migrations', 'device_types'),
    ]

    types_subdir = 'events'

    def load_models(self, apps):
        self.EventType = apps.get_model('irekua_database', 'EventType')
        self.TermType = apps.get_model('irekua_database', 'TermType')
        self.Term = apps.get_model('irekua_database', 'Term')

    def build_object(self, specification):
        icon_path = specification.pop('icon', None)
        term_types = specification.pop('term_types', None)
        should_imply = specification.pop('should_imply', None)

        event_type, _ = self.EventType.objects.get_or_create(**specification)

        if icon_path is not None:
            self.add_icon(event_type, icon_path)

        if term_types is not None:
            self.add_term_types(event_type, term_types)

        if should_imply is not None:
            self.add_should_imply_terms(event_type, should_imply)

    def add_icon(self, event_type, icon_path):
        image = self.load_image(icon_path)
        basename = os.path.basename(icon_path)
        event_type.icon.save(basename, image, save=True)
        image.close()

    def add_term_types(self, event_type, term_types):
        for term_type in term_types:
            term_type = self.TermType.objects.get(name=term_type)
            event_type.term_types.add(term_type)
        event_type.save()

    def add_should_imply_terms(self, event_type, should_imply):
        for term in should_imply:
            term_type = self.TermType.objects.get(name=term['term_type'])
            term = self.Term.objects.get(term_type=term_type, value=term['value'])
            event_type.should_imply.add(term)
        event_type.save()
