import yaml
import sys
import logging
import importlib
import jinja2
from jinja2 import meta
import argparse

from nanostream.node import *
from nanostream.node_classes.network_nodes import *
from nanostream.civis_nodes import *


logging.basicConfig(level=logging.INFO)


def run_pipeline(config_file, module_paths=None):

    if module_paths is not None:
        for path in module_paths.split(':'):
            sys.path.insert(0, path)

    environment = jinja2.Environment()

    logging.info('loading configuration: {config_file}'.format(
        config_file=config_file))

    with open(config_file, 'r') as config_file:
        template = config_file.read()

    template_obj = jinja2.Template(template)
    parsed = environment.parse(template)
    evaluator_functions = meta.find_undeclared_variables(parsed)
    logging.info('found evaluator functions: {evaluator_functions}'.format(
        evaluator_functions=str(evaluator_functions)))

    functions_dict = {}
    for function_name in evaluator_functions:
        components = function_name.split('__')
        if len(components) == 1:
            module = None
            function_name_str = components[0]
            function_obj = globals()[function_name_str]
        else:
            module = '.'.join(components[:-1])
            function_name_str = components[-1]
            module = importlib.import_module(module)
            function = getattr(module, function_name_str)
        functions_dict[function_name] = function()

    post_func_config = template_obj.render(**functions_dict)
    pipeline_config_dict = yaml.load(post_func_config)

    pipeline_name = pipeline_config_dict.get('pipeline_name', None)

    node_dict = {}

    for node_name, node_config in pipeline_config_dict['nodes'].items():
        node_class = globals()[node_config['class']]
        node_config['options'].update({'name': node_name})
        node = node_class(**node_config['options'])
        node_dict[node_name] = node

    for edge in pipeline_config_dict['edges']:
        node_dict[edge['source']] > node_dict[edge['target']]

    list(node_dict.values())[0].global_start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a NanoStream pipeline.')
    parser.add_argument('command', choices=['run', 'dump'])
    parser.add_argument(
        '--filename',
        action='store',
        help='Path to configuration file.')
    parser.add_argument(
        '--module-paths',
        action='store',
        help='Additional paths for loading modules.')
    options = parser.parse_args()

    # Run a pipeline
    if options.command == 'run':
        if options.filename is None:
            raise Exception('Filename is required for run')
        run_pipeline(options.filename, module_paths=options.module_paths)
    # Dump the config file somewhere
    elif options.command == 'dump':
        raise NotImplementedError('Dump is not yet implemented')
    else:
        raise Exception('This should not happen.')