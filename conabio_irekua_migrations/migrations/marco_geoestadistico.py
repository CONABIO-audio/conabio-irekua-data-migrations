from django.db import migrations
from irekua_marco_geoestadistico.migrations.migrate_geostatistical_framework import migrate_geostatistical_framework


class Migration(migrations.Migration):

    dependencies = [
        ('conabio_irekua_migrations', 'collection_types'),
    ]

    operations = [
        migrations.RunPython(migrate_geostatistical_framework),
    ]
