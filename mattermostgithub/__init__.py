import os
import sys
from flask import Flask
app = Flask(__name__)

if 'MGI_CONFIG_FILE' in os.environ:
    module_name = 'mattermostgithub.config'
    file_path = os.environ['MGI_CONFIG_FILE']
    try:
        # python 3
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
    except ImportError:
        # python 2
        import imp
        config = imp.load_source(module_name, file_path)

import mattermostgithub.server
