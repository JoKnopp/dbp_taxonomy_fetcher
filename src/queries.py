PREFIXES = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/page/>
'''

def select_subclass(owl_class):
    if not (owl_class.startswith('dbpedia-owl') or owl_class.startswith('<http://dbpedia.org/ontology/')):
        owl_class = 'dbpedia-owl:' + owl_class
    sel = '''SELECT DISTINCT ?subClass
            WHERE { ?subClass rdfs:subClassOf ''' + owl_class + ' . }'
    return PREFIXES + sel

def select_class_instances(owl_class):
    if not (owl_class.startswith('dbpedia-owl') or owl_class.startswith('<http://dbpedia.org/ontology/')):
        owl_class = 'dbpedia-owl:' + owl_class
    sel = '''SELECT DISTINCT ?Concept
            WHERE { ?Concept rdf:type ''' + owl_class + ' . }'
    return PREFIXES + sel

def get_abstract(dbpedia_resource, lang='en'):
    sel = 'SELECT DISTINCT ?abstract WHERE {' + dbpedia_resource + ''' dbpedia-owl:abstract ?abstract . FILTER ( langMatches( lang(?abstract), "''' + lang + '" ) ) } '
    return PREFIXES + sel
