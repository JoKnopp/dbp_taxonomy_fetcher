#!/usr/bin/python
# -*- coding: UTF-8 -*-

#This file is part of pwrapper.

#pwrapper is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#pwrapper is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with pwrapper. If not, see <http://www.gnu.org/licenses/>.


'''
Module comment

..  moduleauthor:: Johannes Knopp <johannes@informatik.uni-mannheim.de>
'''

from __future__ import absolute_import
from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2011 Johannes Knopp'

import logging
import optparse
import sys
import os
import codecs
import cPickle as pickle
import time #for temporal file name generation

import queries as q
import taxonomy as t

from SPARQLWrapper import SPARQLWrapper, JSON

#the global logger
LOG = logging.Logger(__name__)
LOG.setLevel(logging.DEBUG)

#used sparql endpoint
SPARQL_ENDPOINT = 'http://dbpedia.org/sparql'

def init_optionparser():
    '''Initialise command line parser.'''

    usage = 'Usage: %prog [options] taxonomy_root'

    parser = optparse.OptionParser(usage)

    parser.add_option('-q', '--quiet',
        action='store_true',
        dest='quiet',
        default=False,
        help='Ignore informal output'
    )

    parser.add_option('-d', '--debug',
        default=False,
        action='store_true',
        dest='debug',
        help='Print debug output [default: %default]'
        )
    parser.add_option('--load_taxonomy',
            action='store', default=None,
            dest='tax_file',
            help='Load taxonomy from pickledfile'
        )
    #TODO mandatory, not optional
    parser.add_option('--save_taxonomy',
            action='store', default=None,
            dest='save_tax_file',
            help='Save taxonomy to file in pkl format'
        )
    parser.add_option('--save_abstracts',
            action='store', default=None,
            dest='abstracts_dir',
            help='Save abstracts to txt files in the given directory'
        )


    #Logging related options
    log_options = optparse.OptionGroup(parser,
            'Logging',
            'Specify log file handling.'
    )

    log_level = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    log_options.add_option('--log-file',
                            metavar='FILE',
                            type='string',
                            help='write logs to FILE'
                            )

    log_options.add_option('--log-file-level',
                            help='set log level (' +
                            ', '.join(log_level) +
                            ') [default: %default]',
                            action='store', default='INFO',
                            type='choice', choices=log_level
                            )

    parser.add_option_group(log_options)
    return parser

def init_logging(options):
    '''Initialise logging framework

    :param options: Options obtained from optparse'''

    error = logging.StreamHandler(sys.stderr)
    error.setLevel(logging.ERROR)
    error.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
    LOG.addHandler(error)

    if not options.quiet:
        loglevel = logging.INFO
        console = logging.StreamHandler()
        if options.debug:
            loglevel = logging.DEBUG
        console.setLevel(loglevel)
        console.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
        LOG.addHandler(console)

    if options.log_file:
        log_file_handler = logging.FileHandler(
            options.log_file)
        log_file_handler.setLevel(
            logging.getLevelName(options.log_level))
        log_file_handler.formatter = logging.Formatter(
            '[%(levelname)s]: %(message)s')
        LOG.addHandler(log_file_handler)

    LOG.debug('Logging initialised')


def fire_query(query, endpoint=SPARQL_ENDPOINT, sparql=None):
    try:
        if not sparql:
            sparql = SPARQLWrapper(endpoint)
        assert(isinstance(sparql,SPARQLWrapper))
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.queryAndConvert()
    except Exception as e:
        LOG.error(e)
        return None



def generate_taxonomy_from_class(root_cls):
    LOG.info('generating taxonomy for subtree of "' + root_cls.name + '"')
    owl_classes = [root_cls]
    taxonomy = t.Taxonomy(root_cls)
    ii = 1

    while owl_classes:
        new_owl_classes = []

        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        for cls in owl_classes:
            query = q.select_subclass(cls.name)
            results = fire_query(query, sparql=sparql)
            if not results:
                continue
            LOG.debug(results)
            for var in results['head']['vars']:
                for res in results['results']['bindings']:
                    val = '<' + res[var]['value'] + '>'
                    tcls = t.TClass(val, ii, cls,[])
                    taxonomy.add_class(tcls)
                    cls.add_child(tcls)
                    LOG.debug('Added "{0}" (ii={1}) to taxonomy at {2}'.format(
                        tcls.name, ii, cls.name))
                    new_owl_classes.append(tcls)

        owl_classes = new_owl_classes
        ii += 1

    LOG.info('taxonomy generated')
    return taxonomy


def print_sparql_results(results):
    for var in results['head']['vars']:
        for res in results['results']['bindings']:
            print('var: "' + var + '" – ' + res[var]['value'])


def serialize_object(obj, file_name):
    LOG.info('writing file "' + file_name + '"')
    with open(file_name, 'w') as f:
        try:
            pickle.dump(obj, f)
            LOG.info('file written')
        except IOError as iee:
            LOG.error(iee)


def deserialize_object(file_name):
    LOG.info('loading file "' + file_name + '"')
    with open(file_name, 'r') as f:
        try:
            res = pickle.load(f)
            LOG.info('loaded')
        except IOError as iee:
            LOG.error(iee)
        return res


def find_instances_of_class(cls_name):
    query = q.select_class_instances(cls_name)
    results = fire_query(query)
    instances = []
    if not results:
        return instances
    for res in results['results']['bindings']:
        #Concept is the name of the variable used in queries.py
        instances.append(t.Instance('<' + res['Concept']['value'] + '>'))
    return instances


def add_instances_to_tax_classes(taxonomy):
    LOG.info('adding instances to taxonomy')
    for cls in taxonomy.classes.itervalues():
        for instance in find_instances_of_class(cls.name):
            cls.instances.add(instance)
    LOG.info('done')


def get_abstract(instance):
    qres = fire_query(q.get_abstract(instance.uri))
    abstract = ''
    if qres:
        try:
            abstract = qres['results']['bindings'][0]['abstract']['value']
        except IndexError as ie:
            pass
    return abstract

def add_abstracts_to_instances(taxonomy):
    LOG.info('adding abstracts to instances')
    ii = 0
    tmp_filename = str(time.time()).split('.')[-1] + '_taxonomy.tmp'
    for cls in taxonomy.classes.itervalues():
        for instance in cls.instances:
            if ii % 100 == 0:
                sys.stdout.write('\r'+'adding abstract #{0}'.format(ii))
                sys.stdout.flush()
                if ii % 1000 == 0:
                    sys.stdout.write('\n')
                    serialize_object(taxonomy, tmp_filename)
                    sys.stdout.flush()
            if not hasattr(instance, 'abstract'):
                abstract = get_abstract(instance)
                instance.abstract = abstract
                ii += 1
    LOG.info('done')


def export_abstracts(taxonomy, export_dir):
    if not os.path.exists(export_dir):
        os.mkdir(export_dir)

    LOG.info('exporting abstracts to ' + export_dir)
    if not export_dir.endswith(os.sep):
        export_dir = export_dir + os.sep
    for cls in taxonomy.classes.itervalues():
        for instance in cls.instances:
            if not hasattr(instance, 'abstract'):
                continue
            fname = export_dir + instance.uri.split('/')[-1][:-1] + '.txt'
            with codecs.open(fname, 'w', 'utf-8') as f:
                f.write(instance.abstract)


if __name__ == '__main__':
    parser = init_optionparser()
    (options, args) = parser.parse_args()
    init_logging(options)

    fname = options.tax_file
    save_tax_file = options.save_tax_file
    

    #start from scratch
    if not fname:
        if len(args) != 1:
            LOG.info('wrong number of arguments')
            LOG.info(parser.usage)
            sys.exit(1)

        #args[0]: e.g. '<http://dbpedia.org/ontology/Species>'
        root_cls = t.TClass(args[0])
        taxonomy = generate_taxonomy_from_class(root_cls)
        add_instances_to_tax_classes(taxonomy)
        add_abstracts_to_instances(taxonomy)

    #start with taxonomy file
    else:
        taxonomy = deserialize_object(fname)
    #print(taxonomy)

    #export abstracts to text files in the given directory
    if options.abstracts_dir:
        export_abstracts(taxonomy, options.abstracts_dir)

    #save taxonomy object
    if save_tax_file:
        serialize_object(taxonomy, save_tax_file)
