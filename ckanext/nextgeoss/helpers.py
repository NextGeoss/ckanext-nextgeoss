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