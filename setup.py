import os
from setuptools import setup, find_packages

PACKAGE_NAME = 'rasa-board-server'
DIRNAME = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIRNAME, 'README.md')) as f:
    README = f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name=PACKAGE_NAME,
    version='0.0.1',
    author='Hacko Evgeniy',
    packages=find_packages(exclude=['test_project']),
    package_data={
        '': ['*.json'],
    },
    description='nicecode-module',
    long_description=README,
    include_package_data=True,
    install_requires=[
        'Django==1.11.9',
        'pytz==2017.2',
        'django-model-utils==3.0.0',
        'django-positions==0.5.4',
        'djangorestframework==3.7.0',
        'Pillow==4.1.1',
        'psycopg2==2.7.1',
        'celery==3.1.25',
        'amqp==1.4.9',
        'anyjson==0.3.3',
        'billiard==3.3.0.23',
        'django-extensions==1.7.9',
        'django-jet==1.0.6',
        'django-celery==3.2.1',
        'django-polymorphic',
        'django-phonenumber-field'
    ]
)