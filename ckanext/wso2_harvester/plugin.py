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

import urllib
import urllib2
import logging

from ckan.plugins import toolkit
from ckan.plugins.core import SingletonPlugin, implements
from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestJob, HarvestObject, HarvestGatherError, \
                                    HarvestObjectError
from ckan.logic import ValidationError, NotFound, get_action
from ckan.logic.schema import default_create_package_schema
from ckan.lib.navl.validators import ignore_missing,ignore
from ckan.lib.munge import munge_title_to_name,substitute_ascii_equivalents
from ckanext.edc_schema.forms.dataset_form import EDC_DatasetForm

import ckan.model as model
from ckan.model import Session, Package
import HTMLParser
from ckan.lib.helpers import json
from hashlib import sha1
from pprint import pprint
from ckan.common import  _, request, c

from ckanext.harvest.harvesters.base import HarvesterBase

log = logging.getLogger(__name__)

class WSO2Harvester(HarvesterBase):
    '''
    A WSO2 Harvester
    '''
    implements(IHarvester)

    config = None

    WSO2_COOKIE = ''

    def _get_wso2_login_url(self, apim_url):
        return apim_url.strip('/') + '/publisher/site/blocks/user/login/ajax/login.jag'

    def _get_wso2_api_list_url(self, apim_url):
        return apim_url.strip('/') + '/publisher/site/blocks/listing/ajax/item-list.jag'

    def _get_wso2_api_detail_url(self, apim_url):
        return apim_url.strip('/') + '/publisher/site/blocks/listing/ajax/item-list.jag'

    def _wso2_login(self, apim_url, username, password):
        url = self._get_wso2_login_url(apim_url)
        data = {'action': 'login', 'username': username, 'password': password}
        return self._send_data(url, data)

    def _wso2_get_all_apis(self, apim_url):
        if not self.WSO2_COOKIE:
            raise ContentFetchError('Must login to WSO2 first')

        url = self._get_wso2_api_list_url(apim_url)
        data = {'action': 'getAllAPIs'}
        return self._send_data(url, data)

    def _wso2_get_api_detail(self, apim_url, api_name, api_version, api_provider):
        if not self.WSO2_COOKIE:
            raise ContentFetchError('Must login to WSO2 first')

        url = self._get_wso2_api_detail_url(apim_url)
        data = {'action': 'getAPI', 'name': api_name, 'version': api_version, 'provider': api_provider}
        return self._send_data(url, data)

    '''
    Sends a POST request to the post_url with the data inside post_data
    '''
    def _send_data(self, post_url, post_data):
        data = urllib.urlencode(post_data)
        headers = {}

        if self.WSO2_COOKIE:
            headers['Cookie'] = self.WSO2_COOKIE

        req = urllib2.Request(url=post_url, data=data, headers=headers)
        try:
            content = urllib2.urlopen(req)
        except urllib2.URLError, e:
            raise ContentFetchError(
                'Could not fetch url: %s, error: %s' %
                (url, str(e))
            )
        return content

    def _set_config(self,config_str):
        if config_str:
            self.config = json.loads(config_str)
            if 'api_version' in self.config:
                self.api_version = int(self.config['api_version'])

            log.debug('Using config: %r', self.config)
        else:
            self.config = {}


    def info(self):

        return {
            'name': 'wso2',
            'title': 'WSO2',
            'description': 'A WSO2 store server'
        }

    def validate_config(self, config):

        try:
            if not config:
                raise ValueError('username and password must be set')

            config_obj = json.loads(config)

            if 'username' in config_obj:
                try:
                    isinstance(config_obj['username'], str)
                except ValueError:
                    raise ValueError('username must be a string')
            else:
                raise ValueError('username is required')

            if 'password' in config_obj:
                try:
                    isinstance(config_obj['password'], str)
                except ValueError:
                    raise ValueError('password must be a string')
            else:
                raise ValueError('password is required')

        except ValueError,e:
            raise e

        return config

    def gather_stage(self, harvest_job):

        log.debug('In WSO2Harvester gather_stage (%s)' % harvest_job.source.url)

        self._set_config(harvest_job.source.config)
        config = json.loads(harvest_job.source.config)

        apim_url = harvest_job.source.url
        username = config['username']
        password = config['password']

        try:
            result = self._wso2_login(apim_url, username, password)
            self.WSO2_COOKIE = result.headers['Set-Cookie']
            json_data = json.loads(result.read())
            if(json_data['error'] != False):
                self._save_gather_error('Unable to login to WSO2: %s: username: %s, password: %s' % (json_data['message'], username, password), harvest_job)
                return None
        except ContentFetchError,e:
            self._save_gather_error('Unable to get login URL: %s: %s' % (apim_url, str(e)), harvest_job)
            return None

        try:
            result = self._wso2_get_all_apis(apim_url)
            json_data = json.loads(result.read())

            if(json_data['error'] != False):
                self._save_gather_error('Unable to fetch API list from WSO2: %s' % (json_data['message']), harvest_job)
                return None

            api_list = json_data['apis']
            ids = []
            for api in api_list:
                api_name = api['name']
                log.debug('Gathered API %s', str(api_name))
                id = sha1(api_name).hexdigest()
                obj = HarvestObject(guid=id, job=harvest_job, content=json.dumps(api))
                obj.save()
                ids.append(obj.id)
            return ids

        except ContentFetchError, e:
            self._save_gather_error('Unable to get API List URL: %s: %s' % (apim_url, str(e)), harvest_job)
            return None



    def fetch_stage(self, harvest_object):

        log.debug('In WSO2Harvester fetch_stage (%s)' % harvest_object.source.url)

        self._set_config(harvest_object.job.source.config)

        api = json.loads(harvest_object.content)

        config = json.loads(harvest_object.source.config)
        apim_url = harvest_object.source.url
        username = config['username']
        password = config['password']

        try:
            result = self._wso2_login(apim_url, username, password)
            self.WSO2_COOKIE = result.headers['Set-Cookie']
            json_data = json.loads(result.read())
            if(json_data['error'] != False):
                self._save_object_error('Unable to login to WSO2: %s: username: %s, password: %s' % (json_data['message'], username, password), harvest_object)
                return None
        except ContentFetchError, e:
            self._save_object_error('Unable reach login URL: %s: %s' % (apim_url, str(e)), harvest_object)
            return None

        try:
            result = self._wso2_get_api_detail(apim_url, api['name'], api['version'], api['provider'])
            json_data = json.loads(result.read())
            if(json_data['error'] != False):
                self._save_object_error('Unable to get details for API: %s: %s' % (api['name'], str(e)), harvest_object)
                return None

            # Save the fetched contents in the HarvestObject
            harvest_object.content = json.dumps(json_data['api'])
            harvest_object.save()
            return True

        except ContentFetchError, e:
            self._save_object_error('Unable reach details URL for API: %s: %s' % (api['name'], str(e)), harvest_object)
            return None

    def import_stage(self, harvest_object):

        log.debug('In WSO2Harvester import_stage (%s)' % harvest_object.source.url)

        h = HTMLParser.HTMLParser()

        if not harvest_object:
            log.error('No harvest object received')
            return False

        if harvest_object.content is None:
            self._save_object_error('Empty content for object %s' % harvest_object.id,
                    harvest_object, 'Import')
            return False

        self._set_config(harvest_object.job.source.config)

        try:
            data_dict = json.loads(harvest_object.content)
            config = json.loads(harvest_object.source.config)

            package_dict = {}

            author = model.User.get(config['ckan_user'])
            owner_org = model.Group.get(config['owner_org'])
            org = model.Group.get(config['parent_org'])
            sub_org = model.Group.get(config['owner_org'])
            state = config('edc_state')

            package_dict['id'] = harvest_object.guid
            package_dict['resources'] = []
            package_dict['author'] = author.id
            package_dict['owner_org'] = owner_org.id
            package_dict['title'] = data_dict['name']
            package_dict['notes'] = h.unescape(data_dict['description'])
            #package_dict['tags'] = [{'name': 'WSO2', 'display_name': 'WSO2', 'state': 'active'}]

            # Common extras
            if 'extras' not in package_dict:
                package_dict['extras'] = []

            package_dict['extras'].append({'key': 'harvest_catalogue_name', 'value': harvest_object.source.title, 'state': 'active'})
            package_dict['extras'].append({'key': 'harvest_catalogue_url', 'value': harvest_object.source.url, 'state': 'active'})

            # EDC Fields
            package_dict['type'] = 'WebService'

            if org:
                package_dict['extras'].append({'key': 'org', 'value':org.id, 'state': 'active'})

            if sub_org:
                package_dict['extras'].append({'key': 'sub_org', 'value':sub_org.id, 'state': 'active'})

            if state:
                package_dict['extras'].append({'key': 'edc_state', 'value': state, 'state': 'active'})

            package_dict['extras'].append({'key': 'metadata_visibility', 'value': 'Public', 'state': 'active'})
            package_dict['extras'].append({'key': 'view_audience', 'value': 'Public', 'state': 'active'})
            package_dict['extras'].append({'key': 'download_audience', 'value': 'Public', 'state': 'active'})

            # Add store listing page as resource
            resource_dict = {}
            resource_dict['title'] = data_dict['name']
            resource_dict['name'] = data_dict['name']
            resource_dict['format'] = 'html'
            query_string = { 'name': data_dict['name'], 'version': data_dict['currentDefaultVersion'], 'provider': data_dict['provider'] }
            resource_dict['url'] = harvest_object.source.url.strip('/') + '/store/apis/info?' + urllib.urlencode(query_string)

            package_dict['resources'].append(resource_dict)

            self._create_or_update_package(package_dict, harvest_object)

        except Exception, e:
            self._save_object_error('Error creating package from API %s: %s' % (harvest_object.id, str(e)),
                    harvest_object, 'Import')
            return None

    '''
    This function is almost the same as provided from base.py with a few modifications
    specific to the BCDC instance
    '''
    def _create_or_update_package(self, package_dict, harvest_object):

        try:
            # Check API version
            if self.config:
                try:
                    api_version = int(self.config.get('api_version', 2))
                except ValueError:
                    raise ValueError('api_version must be an integer')

                #TODO: use site user when available
                user_name = self.config.get('user', u'harvest')
            else:
                api_version = 2
                user_name = u'harvest'

            #edc_form = EDC_DatasetForm()
            schema = default_create_package_schema()
            schema['id'] = [ignore_missing, unicode]

            context = {
                'schema': schema,
                'user': user_name,
                'ignore_auth': True,
            }

            if self.config and self.config.get('clean_tags', False):
                tags = package_dict.get('tags', [])
                tags = [munge_tag(t) for t in tags if munge_tag(t) != '']
                tags = list(set(tags))
                package_dict['tags'] = tags

            # Check if package exists
            data_dict = {}
            data_dict['id'] = package_dict['id']
            try:
                existing_package_dict = toolkit.get_action('package_show')(context, data_dict)

                if not 'metadata_modified' in package_dict or package_dict['metadata_modified'] > existing_package_dict.get('metadata_modified') or self.config.get('force_all', False):

                    package_id = toolkit.get_action('package_update')(context, package_dict)
                    log.info('Updated dataset with id %s', package_id)

                else:
                    log.info('Package with GUID %s not updated, skipping...' % harvest_object.guid)
                    return

                # Flag this object as the current one
                harvest_object.package_id = package_id
                harvest_object.current = True
                harvest_object.add()

            except NotFound:
                # Package needs to be created

                # Get rid of auth audit on the context otherwise we'll get an
                # exception
                context.pop('__auth_audit', None)

                # Set name for new package to prevent name conflict, see issue #117
                if package_dict.get('name', None):
                    package_dict['name'] = self._gen_new_name(package_dict['name'])
                else:
                    package_dict['name'] = self._gen_new_name(package_dict['title'])

                log.info('Package with GUID %s does not exist, let\'s create it' % harvest_object.guid)
                harvest_object.current = True
                harvest_object.package_id = package_dict['id']
                # Defer constraints and flush so the dataset can be indexed with
                # the harvest object id (on the after_show hook from the harvester
                # plugin)
                harvest_object.add()

                model.Session.execute('SET CONSTRAINTS harvest_object_package_id_fkey DEFERRED')
                model.Session.flush()

                new_package = toolkit.get_action('package_create')(context, package_dict)

            Session.commit()

            return True

        except ValidationError,e:
            log.exception(e)
            self._save_object_error('Invalid package with GUID %s: %r'%(harvest_object.guid,e.error_dict),harvest_object,'Import')
        except Exception, e:
            log.exception(e)
            self._save_object_error('%r'%e,harvest_object,'Import')

        return None



class ContentFetchError(Exception):
    pass