import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.nextgeoss import helpers


class NextgeossPlugin(plugins.SingletonPlugin):
    ''' Plugin for the NextGEOSS theme.
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'nextgeoss')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'nextgeoss_get_org_title': helpers.get_org_title
        }
