================================================
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

The following configuration options are specific to the Data Catalogue and may not be necessary for all instances:

    `parent_org`: The parent organization/group the datasets will belong to.
    `owner_org`: The organization that the datasets will belong to.

An example configuration is provided here:

```
{
    "username": "wso2-admin",
    "password": "wso2-admin-password",
    "parent_org": "the-parent-organization",
    "owner_org": "the-sub-org",
    "ckan_user": "admin"
}

```

Running the harvester
---------------------

The WSO2 harvester runs like any other harvester, with the gather -> fetch -> import stages.  It should run as per any other harvest job.