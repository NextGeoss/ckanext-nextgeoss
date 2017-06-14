import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper

from ckanext.nextgeoss import helpers


class NextgeossPlugin(plugins.SingletonPlugin):
    ''' Plugin for the NextGEOSS theme.
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'nextgeoss')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'nextgeoss_get_org_title': helpers.get_org_title,
            'nextgeoss_get_org_logo': helpers.get_org_logo
        }

    # IRoutes

    def before_map(self, map):
        controller = 'ckanext.nextgeoss.controller:StaticController'
        with routes.mapper.SubMapper(map, controller=controller) as m:
            m.connect('privacy', '/privacy', action='privacy')
            m.connect('termsandconditions', '/terms-and-conditions',
                      action='termsandconditions')
            m.connect('cookies', '/cookies', action='cookies')
            m.connect('codeofconduct', '/code-of-conduct',
                      action='codeofconduct')
            m.connect('provide', '/provide',
                      action='provide')
            m.connect('use', '/use',
                      action='use')
            m.connect('develop', '/develop',
                      action='develop')

        return map

    def after_map(self, map):
        return map
