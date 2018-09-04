import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper

import ckan.lib.helpers as h

from ckanext.nextgeoss import helpers
from ckan.common import _, c
import ckan.lib.base as base


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

    # ITemplateHelpers

    def get_helpers(self):
        return {
             'nextgeoss_get_jira_script': helpers.get_jira_script,
             'nextgeoss_get_add_feedback_url': helpers.get_add_feedback_url,
             'nextgeoss_get_bug_disclaimer': helpers.get_bug_disclaimer,
             'nextgeoss_get_topic_resources': helpers.topic_resources,
             'nextgeoss_get_value': helpers.get_value,
             'nextgeoss_get_pilot_extras': helpers.get_pilot_extras,
             'harvest_sorted_extras': helpers.harvest_sorted_extras,
             'ng_extra_names': helpers.get_extra_names,
             'ng_extras_to_exclude': helpers.get_extras_to_exclude,
             'ng_get_dataset_thumbnail_path': helpers.get_dataset_thumbnail_path,  # noqa: E501
             'ng_get_from_extras': helpers.get_from_extras,
             'ng_get_source_namespace': helpers.get_source_namespace,
             'get_pkg_dict_dataset_extra': helpers.get_pkg_dict_dataset_extra,
             'nextgeoss_get_site_statistics': helpers.nextgeoss_get_site_statistics
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
        group_controller = 'ckanext.nextgeoss.controllers.group:NextgeossGroupController'  # noqa: E501
        with routes.mapper.SubMapper(map, controller=group_controller) as m:
            m.connect('topic_index', '/topic', action='index')
            m.connect('/topic/list', action='list')
            m.connect('/topic/new', action='new')
            m.connect('topic_action', '/topic/{action}/{id}',
                      requirements=dict(action='|'.join([
                          'edit',
                          'delete',
                          'admins',
                          'member_new',
                          'member_delete',
                          'history'
                          'followers',
                          'follow',
                          'unfollow',
                          'activity',
                      ])))
            m.connect('topic_activity', '/topic/activity/{id}',
                      action='activity', ckan_icon='clock')
            m.connect('topic_read', '/topic/{id}', action='read')
            m.connect('topic_about', '/topic/about/{id}',
                      action='about', ckan_icon='info-circle')
            m.connect('topic_read', '/topic/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('topic_edit', '/topic/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('topic_members', '/topic/members/{id}',
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
            m.connect('private', '/private',
                      action='private')
            m.connect('unauthorized', '/unauthorized',
                      action='unauthorized')

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
        facets_dict['groups'] = _('Topics')
        facets_dict['organization'] = _('Providers')

        return facets_dict

    def dataset_facets(self, facets_dict, package_type):
        """Update the facets used on dataset search pages."""
        return self._update_facets(facets_dict)

    def group_facets(self, facets_dict, group_type, package_type):
        """Update the facets used on group search pages."""
        return self._update_facets(facets_dict)

    def organization_facets(self, facets_dict, organization_type, package_type):  # noqa: E501
        """Update the facets used on organization search pages."""
        return self._update_facets(facets_dict)


# Make the portal private for the beta
# Yes, this is bad.
# Locking down the beta is worse.
# When the beta is over, we can just delete this section.
def private(self, action, **env):
    url = h.current_url()
    if not c.userobj \
        and url != "/user/login" \
        and url != "/user/register" \
        and url != "/private" \
        and not url.startswith("/opensearch") \
        and not url.startswith("/oauth2"):  # noqa: E129

        return h.redirect_to("/private")

    elif not c.userobj \
        or url == "/user/login" \
        or url == "/user/register" \
        or url == "/private" \
        or url.startswith("/opensearch") \
        or url.startswith("/oauth2"):  # noqa: E129

        pass

    elif getattr(c.userobj, "about", "false") != "true" \
        and url != "/user/login" \
        and url != "/user/register" \
        and url != "/unauthorized" \
        and not url.startswith("/opensearch") \
        and not url.startswith("/oauth2"):  # noqa: E129

        return h.redirect_to("/unauthorized")

# Monkeypatch the controllers so that we can lock down the beta.
base.BaseController.__after__ = private  # noqa: E305

# End of private beta code
