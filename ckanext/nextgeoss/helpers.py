from ckan.plugins.toolkit import get_action
from ckan.common import config

def get_org_title(id):
    try:
        org = get_action('organization_show')({}, {'id': id})

        return org.get('title', '')
    except Exception:
        return ''

def get_org_logo(id):
    try:
        org = get_action('organization_show')({}, {'id': id})

        return org.get('image_display_url', '')
    except Exception:
        return ''

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


def get_topic_information(extras):
    idetification_info = []
    identification_info_values = {'title_topic', 'date', 'edition', 'abstract', 'purpose', 'status_topic',
                                  'dateType', 'tags', 'otherConstraints'}

    for extra in extras:
        if extra[0] in identification_info_values:
            print extra[0]
            idetification_info.append({'key': extra[0], 'value': extra[1]})

    return idetification_info


def get_contact_information(extras):
    contact_info = []
    contact_info_values = {'individualName', 'organisationName', 'positionName', 'deliveryPoint', 'city',\
                           'postalCode', 'country', 'electronicMailAddress'}

    for extra in extras:
        if extra[0] in contact_info_values:
            contact_info.append({'key': extra[0], 'value': extra[1]})

    return contact_info


def get_metadata_information(extras):
    metadata_info = []
    metadata_info_values = {'fileIdentifier', 'characterSet', 'CharacterString', 'dateStamp', 'metadataStandardName',\
                           'metadataStandardVersion'}

    for extra in extras:
        if extra[0] in metadata_info_values:
            metadata_info.append({'key': extra[0], 'value': extra[1]})

    return metadata_info


def get_distribution_information(extras):
    distribution_info = []
    distribution_info_values = {'URL', 'protocol', 'name', 'description'}

    for extra in extras:
        if any(ext in extra[0] for ext in distribution_info_values):
            distribution_info.append({'key': extra[0], 'value': extra[1]})

    return distribution_info


def get_spatial_information(extras):
    spatial_info = []
    spatial_info_values = {'numberOfDimensions', 'transformationParameterAvailability'}

    for extra in extras:
        if extra[0] in spatial_info_values:
            spatial_info.append({'key': extra[0], 'value': extra[1]})

    return spatial_info


def get_reference_sys_information(extras):
    reference_sys_info = []
    reference_sys_info_values = ['code']

    for extra in extras:
        if extra[0] in reference_sys_info_values:
            reference_sys_info.append({'key': extra[0], 'value': extra[1]})

    return reference_sys_info