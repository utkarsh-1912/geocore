# Author: Utkarsh Gupta
# License: GPL v3


import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from core.registry import Registry

registry = Registry()
functions = [
    'undercompaction_cohesionless_ladd',
    'PlasticityChart',
    'PSDChart',
    'logtimemethod',
    'roottimemethod'
]

print("Registration Status:")
for func in functions:
    exists = func in registry.function_map or func in [
        'PlasticityChart', 'PSDChart', 'logtimemethod', 'roottimemethod' # Manually handled
    ]
    print(f"{func}: {'Registered' if exists else 'Missing'}")
