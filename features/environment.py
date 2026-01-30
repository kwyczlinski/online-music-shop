# import sys
# import os
# # Ensure the src directory is in the path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.api import create_app

def before_scenario(context, scenario):
    context.app = create_app()
    context.client = context.app.test_client()