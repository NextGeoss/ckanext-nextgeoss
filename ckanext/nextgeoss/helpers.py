from ckan.common import config
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import ckan.logic as logic
import ckan.plugins as p
import ckan.lib.helpers as h
import logging
import ast
import ckan.plugins.toolkit as tk
import datetime
import requests
import json
import re
import urlparse
from ckan.lib.helpers import url_for_static
from ckanext.opensearch import config as opensearch_config

log = logging.getLogger(__name__)

def get_jira_script():
    jira_script = config.get('ckanext.nextgeoss.jira_issue_tracker')
    return jira_script


def get_noa_linker_resources(packages):
    noa_url = config.get('ckanext.nextgeoss.linker_service_base_url')
    noa_user = config.get('ckanext.nextgeoss.linker_service_user')
    noa_password = config.get('ckanext.nextgeoss.linker_service_password')
    noa_package_resources = {}

    if noa_url:
        with FuturesSession(max_workers=25) as session:
            urls = ["{0}/search?q={1}&format=json".format(noa_url, package['name']) for package in packages]
            futures = [session.get(url, auth=(noa_user, noa_password), timeout=2) for url in urls]
            for future in as_completed(futures):
                response = future.result()
                package_query = urlparse.urlparse(response.request.url).query
                package_name = urlparse.parse_qs(package_query)['q'][0]
                package_resources = []
                try:
                    response_body = response.json()
                    response.raise_for_status()
                    # Sometimes `entry` is a dict, sometimes an array, depending on n.o. results
                    results = response_body['feed'].get('entry', [])
                except requests.exceptions.RequestException as e:
                    log.error('Error querying the Noa Linker Service: %s', e.message)
                    results = []

                if isinstance(results, dict):
                    results = [results]

                for entry in results:
                    sources = entry.get('sources', {}).get('link')
                    if isinstance(sources, dict):
                        sources = [sources]
                    for source in sources:
                        package_resources.append(source['href'])
                noa_package_resources[package_name] = package_resources
    else:
        log.info('Configuration for Linker Service is missing.')

    return noa_package_resources


def get_noa_linker_package_resources(dataset_name, testing=False):
    """
    Retrieve the sources of the dataset from the Noa Linker Service.
    """

    noa_url = config.get('ckanext.nextgeoss.linker_service_base_url')
    noa_user = config.get('ckanext.nextgeoss.linker_service_user')
    noa_password = config.get('ckanext.nextgeoss.linker_service_password')
    resources = []

    if noa_url or testing:
        query_url = "{0}/search?q={1}&format=json".format(noa_url, dataset_name)
        try:
            response = requests.get(query_url, auth=(noa_user, noa_password), timeout=2)
            response.raise_for_status()
            response_body = response.json()
            # Sometimes `entry` is a dict, sometimes an array, depending on n.o. results
            results = response_body['feed'].get('entry', [])
            if isinstance(results, dict):
                results = [results]
        except requests.exceptions.RequestException as e:
            log.error('Error querying the Noa Linker Service: %s', e.message)
            results = []

        for entry in results:
            sources = entry.get('sources', {}).get('link')
            if isinstance(sources, dict):
                sources = [sources]
            for source in sources:
                resources.append(source['href'])
    else:
        log.info('Configuration for Linker Service is missing.')

    return resources



def get_add_feedback_url(dataset):
    """
    Create the URL for adding feedback on a dataset via NiMMbus.

    The ID and namespace are currently based on the CKAN instance, but
    in the future they should be updated to use the original ID
    and namespace of the dataset, once we've determined how they'll
    be represented in the metadata.
    """
    feedback_url = 'http://www.opengis.uab.cat/nimmbus/index.htm?target_title={target_title}&target_code={target_code}&target_codespace={target_codespace}&page=ADDFEEDBACK&share_borrower_1=Anonymous'.format(  # noqa: E501
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
    disclaimer = config.get(setting)

    return disclaimer


def topic_resources(extras):
    resources = []
    no_resources = 0

    for extra in extras:
        if extra[0] == 'no_resources':
            no_resources = int(extra[1])

    for extra in extras:
        k, v = extra[0], extra[1]
        if 'resource_' in k and 'Social Media' not in v:
            no_resources = no_resources - 1
            values = ast.literal_eval(extra[1])
            resources.append({'key': extra[0], 'value': str(values)})
    return resources


def get_topics_spatial_information(extras):
    spatial = ''

    for extra in extras:
        if extra[0] == 'extent':
            spatial = str(extra[1])

    print spatial.rstrip('}')

    return spatial


def get_value(resources, key):
    resources_tmp = ast.literal_eval(resources)
    value = ''

    for resource in resources_tmp:
        if resource['key'] == key:
            value = resource['value']

    return value


def get_pilot_extras(extras):
    pilot_extras = []

    for extra in extras:
        k, v = extra[0], extra[1]

        if 'resource' not in k:
            pilot_extras.append({'key': k, 'value': v})

    return pilot_extras


def get_begin_period_topics(extras):
    period = ''

    for extra in extras:
        k, v = extra[0], extra[1]

        if 'begin_position' in k and v != '':
            date =  datetime.datetime.strptime(str(v), '%Y-%m-%d')
            period += date.strftime("%d %B, %Y") + ' '

    return period



def get_end_period_topics(extras):
    period = ''

    for extra in extras:
        k, v = extra[0], extra[1]

        if 'end_position' in k and v != '':
            date =  datetime.datetime.strptime(str(v), '%Y-%m-%d')
            period += date.strftime("%d %B, %Y")

    return period



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
        'uuid': 'UUID',
        'beginposition': 'Sensing start',
        'cloudcoverpercentage': 'Cloud coverage percentage',
        'endposition': 'Sensing end',
        'footprint': 'Footprint',
        'highprobacloudspercentage': 'High probability clouds (%)',
        'identifier': 'Identifier',
        'ingestiondate': 'Ingestion date',
        'timerange_start': 'Timerange Start',
        'timerange_end': 'Timerange End',
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
        'continentalicepercentage': 'Measurement records on continenal ice (%)',  # noqa: E501
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
        'pos': 'Position',
        'file_identifier': 'Identifier',
        'lineage': 'Lineage',
        'purpose': 'Purpose',
        'legal_notice': 'Legal Notice',
        'supplemental_information': 'Supplemental Information',
    }

    return new_names


def get_extras_to_exclude():
    """
    Return a list of extras to exclude from rendered templates using the
    exclude parameter of h.sorted_extras. We may want to grab this list from
    the config in the future.
    """
    extras_to_exclude = [
        'thumbnail', 'codede_download_url', 'codede_product_url', 'noa_product_url',
        'filename', 'collection_description', 'collection_id', 'noa_download_url',
        'spatial', 'scihub_download_url', 'scihub_product_url', 'scihub_thumbnail',
        'format', 'noa_thumbnail', 'noa_manifest_url', 'scihub_manifest_url',
        'gmlfootprint', 'code_manifest_url', 'code_thumbnail_url', 'code_download_url',
        'size', 'code_thumbnail', 'code_product_url',
        'link', 'downloadLink', 'Collection', 'metadata_download',
        'summary', 'product_download', 'thumbnail_download',
        'filename', 'geojsonLink', 'parent_identifier',
        'StartTime',
        'StopTime',
        'acquisition',
        'box',
        'localvalue',
        'published',
        'updated',
        'collection_name',
        'date',
        'product',
        'product_url',
        'noa_expiration_date',
        'uuid',
        'dataset_extra',
        'is_output',
    ]

    return extras_to_exclude


def get_dataset_thumbnail_path(dataset):
    """
    Return the local path for a dataset's thumbnail. If no thumbnail is
    available, return the path to a placeholder image.
    """
    thumbnails_list = ['SENTINEL1_L1_SLC', 'SENTINEL1_L1_GRD', 'SENTINEL2_L1C', 'SENTINEL2_L2A', 'SENTINEL3_SRAL_L2_LAN', \
        'SENTINEL3_OLCI_L1_EFR', 'SENTINEL3_OLCI_L1_ERR', 'SENTINEL3_OLCI_L2_LFR', 'SENTINEL3_OLCI_L2_LRR', \
        'SENTINEL3_SLSTR_L1_RBT', 'SENTINEL3_SLSTR_L2_LST']

    default_image_url = url_for_static('/base/images/placeholder-organization.png')
    image_path = default_image_url
    if dataset['organization']:
        org_id = dataset['organization']['id']
        org_details = logic.get_action('organization_show')({}, {'id': org_id})
        group_image_url = org_details['image_display_url']
        image_path = group_image_url

    collection_id = get_extras_value(dataset['extras'], 'collection_id')
    if collection_id in thumbnails_list:
        collection_image_url = '/{}.jpg'.format(collection_id)
        image_path = collection_image_url

    return image_path


def get_source_namespace(data_dict):
    """Return the source namespace for a product."""
    source = data_dict['organization']['title']

    namespaces = {
        'Sentinel': 'https://scihub.copernicus.eu',
        'Vito': 'http://vito-eodata.be'
    }

    return namespaces.get(source, None)


def nextgeoss_get_site_statistics():
    stats = {}
    stats['dataset_count'] = logic.get_action('package_search')(
        {}, {'include_private': True})['count']
    stats['group_count'] = len(logic.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        logic.get_action('organization_list')({}, {}))
    return stats


def get_collections_count():
    collections = opensearch_config.load_settings("collections_list")

    collections_count = collections.keys()
    collections_count = len(collections_count)

    return collections_count


def get_collection_url(collection_name):
    '''
        Create URL that filters the dataset according to the
        collection_name that has been passed.
    '''
    collection = 'collection_id:' + collection_name

    return "/dataset?collection_name=" + collection_name.replace(' ', '+')


def get_collections_dataset_count(collection_name):
    collection = 'collection_id:' + collection_name
    data_dict = {'q': '',
                 'start': 0,
                 'rows': 20,
                 'ext_bbox': None,
                 'fq': collection }

    results_dict = logic.get_action("package_search")({}, data_dict)

    return results_dict['count']


def get_collections_groups(collection_name):
    collection = 'collection_id:' + collection_name
    data_dict = {'q': '',
                 'start': 0,
                 'rows': 20,
                 'ext_bbox': None,
                 'fq': collection }

    results_dict = logic.get_action("package_search")({}, data_dict)
    results = results_dict['results']
    groups_list = []
    groups_tmp = ''

    for result in results:
        if result.get('groups') != []:
            groups = result.get('groups')
            for group in groups:
                if group['title'] not in groups_tmp:
                    groups_tmp += group['title']
                    groups_list.append({'title': group['title'], 'name': group['name']})

    return groups_list


def nextgeoss_get_facet_title(name):
    '''Deprecated in ckan 2.0 '''
    # if this is set in the config use this
    config_title = config.get('search.facets.%s.title' % name)
    if config_title:
        return config_title

    facet_titles = {'organization': _('Organizations'),
                    'groups': _('Groups'),
                    'tags': _('Tags')}

    return facet_titles.get(name, name.capitalize())


def get_default_slider_values():
    '''Returns the earliest collection date from package_search'''

    data_dict = {
            'sort': 'begin-collection_date asc',
            'rows': 1,
            'q': 'begin-collection_date:[* TO *]',
    }
    result = p.toolkit.get_action('package_search')({}, data_dict)['results']
    if len(result) == 1:
        date = filter(lambda x: x['key'] == 'begin-collection_date',
                result[0].get('extras', []))
        begin = date[0]['value']
    else:
        begin = datetime.date.today().isoformat()

    data_dict = {
            'sort': 'end-collection_date desc',
            'rows': 1,
            'q': 'end-collection_date:[* TO *]',
    }
    result = p.toolkit.get_action('package_search')({}, data_dict)['results']
    if len(result) == 1:
        date = filter(lambda x: x['key'] == 'end-collection_date',
                result[0].get('extras', []))
        end = date[0]['value']
    else:
        end = datetime.date.today().isoformat()
    return begin, end


def get_date_url_param():
    params = ['', '']
    for k, v in tk.request.params.items():
        if k == 'ext_begin_date':
            params[0] = v
        elif k == 'ext_end_date':
            params[1] = v
        else:
            continue
    return params


DEFAULT_SEARCH_NAMES = u'timerange_start timerange_end'

def search_params():
    u'''Returns a list of the current search names'''
    return config.get(u'search.search_param', DEFAULT_SEARCH_NAMES).split()


def get_group_collection_count(group):
    group_collections = []

    if 'extras' in group:
        group_extras = group['extras']

        for extra in group_extras:
            if extra['key'] == 'collections':
                col_value = extra['value'].split(", ")
                for a in col_value:
                    group_collections.append(a)

    collections = []

    for collection_id in group_collections:
        item = collection_information(collection_id)
        collections.append(item)

    return len(collections)


def collection_information(collection_id=None):
    collections = opensearch_config.load_settings("collections_list")
    collection_items = collections.items()

    for collection in collection_items:
        if collection[0] == collection_id:
            return dict(collection[1])


def get_extras_value(extras, extras_key):
    '''
        Return the value from extras from a given key.
    '''
    value = ''

    for extra in extras:
        if extra['key'] == extras_key:
            value = extra['value']

    return value


def generate_opensearch_query(params):
    query = '/opensearch/search.atom?'

    if 'collection_name' in params:
        collection_name = params['collection_name']

        collections = opensearch_config.load_settings("collections_list")
        collection_items = collections.items()

        for collection in collection_items:
            collection_items = collection[1].items()
            if collection_name in collection[1].items()[0]:
                query = query + 'productType=' + collection[0]

        for param in params:
            if param != 'collection_name':
                param_tmp = ''
                if param == 'polarisationChannels':
                    param_tmp = 'polarisation'
                elif param == "swathIdentifier":
                    param_tmp = "swath"
                elif param == "orbitDirection":
                    param_tmp = "orbit_direction"
                elif param == "swathIdentifier":
                    param_tmp = "swath"
                elif param == "OrbitDirection":
                    param_tmp = "orbit_direction"
                elif param == "TransmitterReceiverPolarisation":
                    param_tmp = "polarisation"
                elif param == 'Swath':
                    param_tmp = "swath"
                elif param == 'ext_bbox':
                    param_tmp = "bbox"
                else:
                    param_tmp = param

                if ' ' in params[param]:
                    value = '"' + params[param] + '"'
                else:
                    value = params[param]

                query = query + '&' + param_tmp + '=' + value
    else:
        for param in params:
            if param == 'ext_bbox':
                param_tmp = "bbox"
                query = query + '&' + param_tmp + '=' + params[param]
            else:
                query = query + '&' + param + '=' + params[param]

    return query


def get_featured_groups_list():
    '''
        Returns a list of groups that are setup as featured_groups
        in the configuration file.
    '''
    parent_groups = []
    group_list = config.get('ckan.featured_groups').split()

    if group_list is not None:
        groups = h.get_featured_groups(count=40)

        for group in groups:
            if group['name'] in group_list:
                parent_groups.append(group)

    return parent_groups


def get_topic_output_data(datasets):
    topic_datasets = []

    for dataset in datasets:
        for d in dataset['extras']:
            if d['key'] == 'is_output' and d['value'] == 'True':
                print 'in'
                topic_datasets.append(dataset)

    return topic_datasets