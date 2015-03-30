'''
 Copyright 2015 Province of British Columbia

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and limitations under the License.
'''

from setuptools import setup, find_packages
import sys, os

version = '1.0'

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
