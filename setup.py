from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-wso2-harvester',
    version=version,
    description="A harvester extension for harvesting WSO2 store APIs",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Devin Lumley',
    author_email='devin@highwaythreesolutions.com',
    url='highwaythreesolutions.com',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.wso2_harvester'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        wso2_harvester=ckanext.wso2_harvester.plugin:WSO2Harvester
    ''',
)
