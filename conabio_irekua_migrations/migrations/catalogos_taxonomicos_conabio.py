import logging

from django.db import migrations
from django.db import transaction
from tqdm import tqdm

import solr_conabio.solr_api as solr


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Catálogos Taxonómicos')


HOST = 'http://snmb.conabio.gob.mx'
COLLECTION = 'taxonomia'
ROWS_PER_PETITION = 1000

TERM_FMT = (
    'Term type: {type}\n'
    '  term: {term}\n'
    '  parents: {parents}\n'
    '  common names: {common}\n'
    '  synonyms: {synonyms}'
)
TERM_METADATA_SCHEMA = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://example.com/term_metadata_schema.json",
    "type": "object",
    "title": "Esquema de metadatos para términos taxonómicos",
    "required": [
        "id",
        "version",
        "origin"
    ],
    "properties": {
        "id": {
            "$id": "#/properties/id",
            "type": "string",
            "title": "id",
            "default": "",
            "examples": [
                "term.id"
            ],
            "pattern": "^(.*)$"
        },
        "version": {
            "$id": "#/properties/version",
            "type": "string",
            "title": "version",
            "default": "",
            "examples": [
                "term.version"
            ],
            "pattern": "^(.*)$"
        },
        "origin": {
            "$id": "#/properties/origin",
            "type": "string",
            "title": "origen",
            "default": "",
            "examples": [
                "juancarlos-catálogos"
            ],
            "pattern": "^(.*)$"
        }
    }
}

@transaction.atomic
def update_database(apps, schema_editor):
    db_models = get_database_models(apps)
    data = get_all_data()
    terms = parse_data(data)
    term_pk_map = create_all_terms(terms, db_models)
    create_all_entailments(terms, term_pk_map, db_models)


class Migration(migrations.Migration):

    dependencies = [
        ('irekua_database', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_database),
    ]


def parse_data(data):
    logger.info('Parsing data...')
    terms = {
        str(datum['id']): Term(datum)
        for datum in data
        if datum['nombre']
    }
    logger.info('done.')
    return terms


def get_all_data(num_rows=ROWS_PER_PETITION):
    total_rows = get_num_rows()

    fl = [
        'id',
        'categoria_taxonomica',
        'nombre',
        'ascendentes',
        'nombres_comunes',
        'subcategoria_taxonomica',
        'sinonimos',
        'id_asc',
        '_version_'
    ]

    logger.info('Getting data...')
    data = []
    for start in tqdm(range(0, total_rows, num_rows)):
        response = solr.query(HOST, COLLECTION, rows=num_rows, start=start, fl=fl)
        data += response['response']['docs']

    logger.info('done.')
    return data


def get_num_rows():
    response = solr.query(HOST, COLLECTION, rows=0)
    return response['response']['numFound']


def create_all_terms(all_terms, db_models):
    pk_map = {}

    logger.info('Creating terms...')
    for term in tqdm(all_terms.values()):
        db_term = process_term(all_terms, term, db_models)
        pk_map[term.id] = db_term
    logger.info('done')

    return pk_map


def process_term(all_terms, term, db_models):
    term_type = get_term_type(term.term_type, db_models)

    try:
        scope = all_terms[term.scope].term
    except KeyError:
        logger.error('No scope for {}'.format(term.scope))
        scope = None

    db_term = create_term(
        term_type,
        term.term,
        scope,
        term.metadata,
        db_models)

    if term.synonyms:
        create_synonyms(all_terms, term, db_term, db_models)

    if term.common_names:
        create_common_names(all_terms, term, db_term, db_models)

    return db_term


TERMS = {}
def create_term(term_type, value, scope, metadata, db_models):
    if (term_type.name, value, scope) in TERMS:
        return TERMS[(term_type.name, value, scope)]

    if scope is None:
        db_term, _ = db_models.Term.objects.get_or_create(
            term_type=term_type,
            value=value,
            defaults={
                'metadata': metadata
            }
        )
        TERMS[(term_type.name, value, scope)] = db_term
        return db_term

    db_term, _ = db_models.Term.objects.get_or_create(
        term_type=term_type,
        value=value,
        scope=scope,
        defaults={
            'metadata': metadata
        })
    TERMS[(term_type.name, value, scope)] = db_term
    return db_term


def create_common_names(all_terms, term, db_term, db_models):
    common_name_type = get_term_type('nombre común', db_models)

    try:
        scope = all_terms[term.scope].term
    except KeyError:
        logger.error('No scope for term {}'.format(term.scope))
        scope = None

    for common_name in term.common_names:
        common_name_term = create_term(
            common_name_type,
            common_name,
            scope,
            term.metadata,
            db_models)
        term.common_names_terms[common_name_term.pk] = common_name_term
        create_entailment(common_name_term, db_term, db_models)


TERM_TYPES = {}
def get_term_type(term_type, db_models):
    if term_type not in TERM_TYPES:
        db_term_type, _ = db_models.TermType.objects.get_or_create(
            name=term_type,
            defaults={
                'description': 'Nivel taxonómico: {}'.format(term_type),
                'is_categorical': True,
                'metadata_schema': TERM_METADATA_SCHEMA,
                'synonym_metadata_schema': TERM_METADATA_SCHEMA
            }
        )
        TERM_TYPES[term_type] = db_term_type
        return db_term_type

    return TERM_TYPES[term_type]


def create_synonyms(all_terms, term, db_term, db_models):
    term_type = db_term.term_type

    try:
        scope = all_terms[term.scope].term
    except KeyError:
        logger.error('No scope for term {}'.format(term.scope))
        scope = None

    for synonym in term.synonyms:
        synonym_term = create_term(
            term_type,
            synonym,
            scope,
            term.metadata,
            db_models)
        term.synonyms_terms[synonym_term.pk] = synonym_term
        synonym, _ = create_synonym(synonym_term, db_term, term.metadata, db_models)


def create_synonym(source, target, metadata, db_models):
    return db_models.Synonym.objects.get_or_create(
        source=source,
        target=target,
        defaults={
            'metadata': metadata
        }
    )


def create_all_entailments(terms, mapping, db_models):
    logger.info('Creating entailments...')
    for term in tqdm(terms.values()):
        create_term_entailments(term, mapping, db_models)
    logger.info('done.')


def create_term_entailments(term, mapping, db_models):
    db_term = mapping[term.id]

    for parent_id in term.parents:
        try:
            parent_term = mapping[parent_id]
            create_entailment(db_term, parent_term, db_models)

            for synonym in term.synonyms_terms.values():
                create_entailment(synonym, parent_term, db_models)

            for common_name in term.common_names_terms.values():
                create_entailment(common_name, parent_term, db_models)
        except KeyError:
            pass



def create_entailment(source, target, db_models):
    check_entailment_type(source, target, db_models)
    return db_models.Entailment.objects.get_or_create(
        source=source,
        target=target)


ENTAILMENT_TYPES = {}
def check_entailment_type(source, target, db_models):
    label = (source.term_type.pk, target.term_type.pk)

    if label not in ENTAILMENT_TYPES:
        entailment_type, _ = db_models.EntailmentType.objects.get_or_create(
            source_type=source.term_type,
            target_type=target.term_type)
        ENTAILMENT_TYPES[label] = entailment_type

    return ENTAILMENT_TYPES[label]


def get_database_models(apps):
    class DBModels(object):
        def __init__(self, apps):
            self.EntailmentType = apps.get_model('irekua_database', 'EntailmentType')
            self.Entailment = apps.get_model('irekua_database', 'Entailment')
            self.Term = apps.get_model('irekua_database', 'Term')
            self.TermType = apps.get_model('irekua_database', 'TermType')
            self.Synonym = apps.get_model('irekua_database', 'Synonym')

    return DBModels(apps)


class Term(object):
    def __init__(self, data):
        self.id = str(data['id'])

        try:
            self.term_type = data['subcategoria_taxonomica']
        except KeyError:
            try:
                self.term_type = data['categoria_taxonomica']
            except KeyError:
                self.term_type = None
                logger.error('No term type for {}'.format(data))

        self.term = data['nombre']
        self.version = data['_version_']

        self.common_names = data.get('nombres_comunes', [])
        self.synonyms = data.get('sinonimos', [])
        self.scope = str(data.get('id_asc', ''))

        self.parents = [
            str(sid) for sid in data['ascendentes'].split(',')
            if str(sid) != str(self.id)
        ]

        self.parents_terms = {}
        self.synonyms_terms = {}
        self.common_names_terms = {}

    @property
    def metadata(self):
        return   {
            'id': str(self.id),
            'version': str(self.version),
            'origin': 'juancarlos-catálogos'
        }

    def __str__(self):
        return TERM_FMT.format(
            type=self.term_type,
            term=self.term,
            parents=str(self.parents),
            common=str(self.common_names),
            synonyms=str(self.synonyms))

    def __repr__(self):
        return str(self)
