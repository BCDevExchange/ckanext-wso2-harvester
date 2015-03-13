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

#### Missing Fields from WSO2

- License
- Resource Status

##### Contact Information

There are multiple contact entries permitted and at least one is required.

- Name
- Email
- Organization
- Sub-Organization

###### Access & Security

- Security Classification
- Has a PIA been completed?

###### Resources

- Resource Storage Format
