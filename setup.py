from setuptools import find_packages, setup

setup(
    name='mfnh',
    version='0.0.0-dev',
    description='media scanning',
    packages=find_packages(),
    install_requires=[
        'jinja2',
        'pycountry',
        'sqlalchemy',
        'tmdbsimple',
    ]
)
