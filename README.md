<a rel="Exploration" href="https://github.com/BCDevExchange/docs/blob/master/discussion/projectstates.md"><img alt="Being designed and built, but in the lab. May change, disappear, or be buggy." style="border-width:0" src="http://bcdevexchange.org/badge/2.svg" title="Being designed and built, but in the lab. May change, disappear, or be buggy." /></a>

ckanext-wso2-harvester - WSO2 Harvester for CKAN
================================================

This extension provides a WSO2 harvester using the [ckanext-harvest](https://github.com/ckan/ckanext-harvest) extension for CKAN.

Requirements
------------

[ckanext-harvest](https://github.com/ckan/ckanext-harvest)


Installation
------------

1. Install the extension as you would any other extension, i.e. using `setup.py`.
2. Add `wso2_harvester` to your `ckan.plugins` inside your configuration file.

Configuring the harvester
-------------------------

After installing the extension, a 'WSO2' harvester option should appear under "Source type" when adding a new harvester.  There are a few configuration options required by the extension:

    `username`: This is the username to login into WSO2.  Requires administrator privileges.
    `password`: The password for that username.
    `ckan_user`: The CKAN user the harvester will add datasets under.

The following configuration options are specific to the Data Catalogue CKAN instance and may not be necessary for all instances:

    `edc_state`: The state the dataset will be after import.  e.g. "DRAFT", "PENDING PUBLISH", "PUBLISHED", etc.
    `parent_org`: The parent organization/group the datasets will belong to.
    `owner_org`: The organization that the datasets will belong to.

An example configuration is provided here:

```
{
    "username": "wso2-admin",
    "password": "wso2-admin-password",
    "parent_org": "the-parent-organization",
    "owner_org": "the-sub-org",
    "edc_state": "PENDING PUBLISH",
    "ckan_user": "admin"
}

```

Running the harvester
---------------------

The WSO2 harvester runs like any other harvester, with the gather -> fetch -> import stages.  It should run as per any other harvest job.

Limitations for the Data Catalogue
----------------------------------

The following limitations are only applicable to the Data Catalogue CKAN instance.  Other instances of CKAN will differ based on how (or if) the schema was changed.

### Missing Fields from WSO2

The following fields are not present in WSO2 and as such are not imported when the harvester runs.  These fields are marked as required in the schema and require manual updating.

- License
- Resource Status

#### Contact Information

There are multiple contact entries permitted and at least one is required.

- Name
- Email
- Organization
- Sub-Organization

#### Access & Security

- Security Classification
- Has a PIA been completed?

#### Resources

- Resource Storage Format

#### License
```
     Copyright 2015 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at 

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
```
