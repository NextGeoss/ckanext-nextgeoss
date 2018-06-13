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


def harvest_sorted_extras(package_extras, auto_clean=False, subs=None, exclude=None):
    ''' Used for outputting package extras
    :param package_extras: the package extras
    :type package_extras: dict
    :param auto_clean: If true capitalize and replace -_ with spaces
    :type auto_clean: bool
    :param subs: substitutes to use instead of given keys
    :type subs: dict {'key': 'replacement'}
    :param exclude: keys to exclude
    :type exclude: list of strings
    '''

    # If exclude is not supplied use values defined in the config
    if not exclude:
        exclude = config.get('package_hide_extras', [])
    output = []
    for extra in sorted(package_extras, key=lambda x: x['key']):
        if extra.get('state') == 'deleted':
            continue
        extras_tmp = ast.literal_eval(extra['value'])

        for ext in extras_tmp:
            k, v = ext['key'], ext['value']
            if k in exclude:
                continue
            if subs and k in subs:
                k = subs[k]
            elif auto_clean:
                k = k.replace('_', ' ').replace('-', ' ').title()
            if isinstance(v, (list, tuple)):
                v = ", ".join(map(unicode, v))
            output.append((k, v))
return output