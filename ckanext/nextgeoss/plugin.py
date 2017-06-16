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
        # Rename organizations
        map.redirect('/organization', '/provider',
                     _redirect_code='301 Moved Permanently')
        map.redirect('/organization/{url:.*}', '/provider/{url}',
                     _redirect_code='301 Moved Permanently')
        org_controller = 'ckan.controllers.organization:OrganizationController'
        with routes.mapper.SubMapper(map, controller=org_controller) as m:
            m.connect('providers_index', '/provider', action='index')
            m.connect('/provider/list', action='list')
            m.connect('/provider/new', action='new')
            m.connect('/provider/{action}/{id}',
                      requirements=dict(action='|'.join([
                          'delete',
                          'admins',
                          'member_new',
                          'member_delete',
                          'history'
                          'followers',
                          'follow',
                          'unfollow',
                      ])))
            m.connect('provider_activity', '/provider/activity/{id}',
                      action='activity', ckan_icon='time')
            m.connect('provider_read', '/provider/{id}', action='read')
            m.connect('provider_about', '/provider/about/{id}',
                      action='about', ckan_icon='info-sign')
            m.connect('provider_read', '/provider/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('provider_edit', '/provider/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('provider_members', '/provider/edit_members/{id}',
                      action='members', ckan_icon='group')
            m.connect('provider_bulk_process',
                      '/provider/bulk_process/{id}',
                      action='bulk_process', ckan_icon='sitemap')

        # Add static pages
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
