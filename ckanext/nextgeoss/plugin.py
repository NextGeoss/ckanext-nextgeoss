import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper

from ckanext.nextgeoss import helpers
from ckan.common import _


class NextgeossPlugin(plugins.SingletonPlugin):
    ''' Plugin for the NextGEOSS theme.
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IFacets)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'nextgeoss')
        toolkit.add_resource('vendor', '')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'nextgeoss_get_org_title': helpers.get_org_title,
            'nextgeoss_get_org_logo': helpers.get_org_logo,
            'nextgeoss_get_jira_script': helpers.get_jira_script,
            'nextgeoss_get_add_feedback_url': helpers.get_add_feedback_url,
            'nextgeoss_get_bug_disclaimer': helpers.get_bug_disclaimer
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
            m.connect('provider_index', '/provider', action='index')
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

        # Rename groups
        map.redirect('/group', '/topic',
                     _redirect_code='301 Moved Permanently')
        map.redirect('/group/{url:.*}', '/topic/{url}',
                     _redirect_code='301 Moved Permanently')
        group_controller = 'ckanext.nextgeoss.controllers.group:NextgeossGroupController'
        with routes.mapper.SubMapper(map, controller=group_controller) as m:
            m.connect('topic_index', '/topic', action='index')
            m.connect('/topic/list', action='list')
            m.connect('/topic/new', action='new')
            m.connect('/topic/{action}/{id}',
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
            m.connect('topic_activity', '/topic/activity/{id}',
                      action='activity', ckan_icon='time')
            m.connect('topic_read', '/topic/{id}', action='read')
            m.connect('topic_about', '/topic/about/{id}',
                      action='about', ckan_icon='info-sign')
            m.connect('topic_read', '/topic/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('topic_edit', '/topic/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('topic_members', '/topic/edit_members/{id}',
                      action='members', ckan_icon='group')
            m.connect('topic_bulk_process',
                      '/topic/bulk_process/{id}',
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


    # IFacets

    def _update_facets(self, facets_dict):
      """
      Make it easier to consistently update the various
      facets_dicts. facets_dict will be an ordered dictionary,
      so we need to preserve the order when we update.
      """
      print(facets_dict)
      facets_dict['groups'] = _('Topics')
      facets_dict['organization'] = _('Providers')

      return facets_dict

    def dataset_facets(self, facets_dict, package_type):
      """Update the facets used on dataset search pages."""
      return self._update_facets(facets_dict)

    def group_facets(self, facets_dict, group_type, package_type):
      """Update the facets used on group search pages."""
      return self._update_facets(facets_dict)

    def organization_facets(self, facets_dict, organization_type, package_type):
      """Update the facets used on organization search pages."""
      return self._update_facets(facets_dict)
