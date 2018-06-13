from ckan.plugins.toolkit import get_action
from ckan.common import config
import ast

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
            import ast
            values = ast.literal_eval(extra[1])
            resources.append({'key': extra[0], 'value': str(values)})
    return resources


def get_value(resources, key):
    import ast
    resources_tmp = ast.literal_eval(resources)
    value = ''

    for resource in resources_tmp:
        if resource['key'] == key:
            value = resource['value']

    return value


def get_pilot_extras(extras):
    pilot_extras = []
    print type(pilot_extras)
    skip = {'resource_'}

    for extra in extras:
        k, v = extra[0], extra[1]

        if 'resource' not in k:
            pilot_extras.append({'key': k, 'value': v})
            print pilot_extras
    print type(pilot_extras)
    return pilot_extras