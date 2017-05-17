import os
import sys
from flask import Flask
app = Flask(__name__)

if os.environ.get('MGI_CONFIG_FILE'):
    module_name = "mattermostgithub.config"
    file_path = os.environ.get('MGI_CONFIG_FILE')
    try:
        # python 3
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
    except:
        # python 2
        import imp
        config = imp.load_source('mattermostgithub.config', file_path)

import mattermostgithub.server
