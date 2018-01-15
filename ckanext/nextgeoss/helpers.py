from ckan.plugins.toolkit import get_action
from ckan.common import config
from ckan.lib.helpers import sorted_extras

def get_jira_script():
    jira_script = config.get('ckanext.nextgeoss.jira_issue_tracker')
    return jira_script


def get_add_feedback_url(dataset):
    """
    Create the URL for adding feedback on a dataset via NiMMbus.

    The ID and namespace are currently based on the CKAN instance, but
    in the future they should be updated to use the original ID
    and namespace of the dataset, once we've determined how they'll
    be represented in the metadata.
    """
    feedback_url = 'http://www.opengis.uab.cat/nimmbus/index.htm?target_title={target_title}&target_code={target_code}&target_codespace={target_codespace}&page=ADDFEEDBACK&share_borrower_1=Anonymous'.format(
        target_title=dataset['title'],
        target_code=dataset['id'],
        target_codespace=config.get('ckan.site_url'))

    return feedback_url


def get_bug_disclaimer():
    """
    Get the text of the disclaimer that will appear beneath the
    issue tracker banner while waiting for it to load (or instead
    of the banner in case the script does not load at all).
    """
    setting = 'ckanext.nextgeoss.bug_disclaimer'
    default = 'This is a testing portal. Click here to submit a bug.'
    disclaimer = config.get(setting, default)

    return disclaimer


def get_extra_names():
    """
    Return a dictionary of new names for use with the subs parameter of
    h.sorted_extras. We may want to grab these names from the config
    in the future.
    """
    new_names = {
        'CloudCoverage': 'Cloud Coverage',
        'FamilyName': 'Family Name',
        'InstrumentFamilyName': 'Instrument Family Name',
        'InstrumentMode': 'Instrument Mode',
        'InstrumentName': 'Instrument Name',
        'OrbitDirection': 'Orbit Direction',
        'ProductType': 'Product Type',
        'StartTime': 'Start Time',
        'StopTime': 'Stop Time',
        'uuid': 'UUID',
        'beginposition': 'Sensing start',
        'cloudcoverpercentage': 'Cloud coverage percentage',
        'endposition': 'Sensing end',
        'footprint': 'Footprint',
        'highprobacloudspercentage': 'High probability clouds (%)',
        'identifier': 'Identifier',
        'ingestiondate': 'Ingestion date',
        'instrumentname': 'Instrument name',
        'instrumentshortname': 'Instrument abbreviation',
        'mediumprobacloudspercentage': 'Medium probability clouds (%)',
        'notvegetatedpercentage': 'Non-vegetated percentage',
        'orbitdirection': 'Orbit direction (start)',
        'orbitnumber': 'Orbit number (start)',
        'platformidentifier': 'Platform identifier',
        'platformname': 'Platform name',
        'platformserialidentifier': 'Platform serial identifier',
        'processingbaseline': 'Processing baseline',
        'processinglevel': 'Processing level',
        'producttype': 'Product type',
        'relativeorbitnumber': 'Start relative orbit number',
        's2datatakeid': 'S2 datatke id',
        'sensoroperationalmode': 'Sensor operational mode',
        'snowicepercentage': 'Snow/ice percentage',
        'unclassifiedpercentage': 'Unclassified percentage',
        'vegetationpercentage': 'Vegetation percentage',
        'waterpercentage': 'Water percentage',
        'missiondatatakeid': 'Mission datatake id',
        'lastorbitnumber': 'Orbit number (stop)',
        'lastrelativeorbitnumber': 'Stop relative orbit number',
        'slicenumber': 'Slice number',
        'acquisitiontype': 'Acquisition type',
        'polarisationmode': 'Polarisation mode',
        'productclass': 'Product class',
        'productconsolidation': 'Product consolidation',
        'status': 'Status',
        'swathidentifier': 'Instrument swath',
        'lrmpercentage': 'Measurement records in LRM mode (%)',
        'sarpercentage': 'Measurement records in SAR mode (%)',
        'closedseapercentage': 'Measurement records on closed sea (%)',
        'continentalicepercentage': 'Measurement records on continenal ice (%)',
        'landpercentage': 'Measurement records on land (%)',
        'openseapercentage': 'Measurement records on open sea (%)',
        'mode': 'Mode',
        'onlinequalitycheck': 'Online quality check',
        'lastorbitdirection': 'Orbit direction (stop)',
        'pduduration': 'PDU duration',
        'passnumber': 'Pass number (start)',
        'lastpassnumber': 'Pass number (stop)',
        'passdirection': 'Pass direction (start)',
        'lastpassdirection': 'Pass direction',
        'procfacilityorg': 'Processing facility organization',
        'processinglevel': 'Processing level',
        'processingname': 'Processing name',
        'productlevel': 'Product level',
        'relorbitdir': 'Relative orbit direction (start)',
        'lastrelorbitdirection': 'Relative orbit direction (stop)',
        'relpassnumber': 'Relative pass number (start)',
        'lastrelpassnumber': 'Relative pass number (stop)',
        'relpassdirection': 'Relative pass direction (start)',
        'lastrelpassdirection': 'Relative pass direction (stop)',
        'timeliness': 'Timeliness category',
        'tileid': 'Tile identifier',
        'hv_order_tileid': 'HV order tile ID',
        'procfacilityname': 'Processing facility',
        'acquisitionparameters': 'Acquisition parameters',
        'parentidentifier': 'Parent identifier',
        'sensortype': 'Sensor type',
        'snowcoverpercentage': 'Snow cover percentage',
        'productinformation': 'Product information',
        'referencesystemidentifier': 'Reference system identifier',
        'resulttime': 'Result time',
        'timeinstant': 'Time instant',
        'timeposition': 'Time position',
        'pos': 'Position'
    }

    return new_names


def get_extras_to_exclude():
    """
    Return a list of extras to exclude from rendered templates using the
    exclude parameter of h.sorted_extras. We may want to grab this list from
    the config in the future.
    """
    extras_to_exclude = [
        'thumbnail',
        'filename',
        'spatial',
        'format',
        'gmlfootprint',
        'size',
        'link',
        'summary',
        'filename',
        'acquisition',
        'thumbanil',
        'box',
        'localvalue',
        'published',
        'updated',
        'collection_name',
        'date',
        'product'
    ]

    return extras_to_exclude


def get_dataset_thumbnail_path(dataset):
    """
    Return the local path for a dataset's thumbnail. If no thumbnail is
    available, return the path to a placeholder image.
    """
    extras = {extra['key']: extra['value'] for extra in dataset['extras']}

    if dataset['organization']['title'] == 'Vito':
        if 'thumbnail' in extras or 'thumbanil' in extras and 'identifier' in extras:
            return '/thumbnails/{}.png'.format(extras['identifier'])
        else:
            return '/base/images/placeholder-image.png'
    elif dataset['organization']['title'] == 'Sentinel':
        if 'thumbnail' in extras and 'uuid' in extras:
            return '/thumbnails/{}.jpg'.format(extras['uuid'])
        else:
            return '/base/images/placeholder-image.png'
    else:
        return '/base/images/placeholder-image.png'


def get_from_extras(data_dict, key, alt_value=None):
    """Return the value of a key in the extras list, or an alternate value."""
    extras = data_dict.get('extras')

    for extra in extras:
        if extra['key'] == key:
            return extra['value']

    return alt_value


def get_source_namespace(data_dict):
    """Return the source namespace for a product."""
    source = data_dict['organization']['title']

    namespaces = {
        'Sentinel': 'https://scihub.copernicus.eu',
        'Vito': 'http://vito-eodata.be'
    }

    return namespaces.get(source, None)
