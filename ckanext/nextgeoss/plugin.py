import ast
import json

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper

import ckan.lib.helpers as h

from ckanext.nextgeoss import helpers
from ckan.common import _, c, config
import ckan.lib.base as base

import shapely
import shapely.geometry


class NextgeossPlugin(plugins.SingletonPlugin):
    ''' Plugin for the NextGEOSS theme.
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'nextgeoss')
        toolkit.add_resource('fanstatic', 'nextgeoss_read_more_paragraph')

    # ITemplateHelpers

    def get_helpers(self):
        return {
             'nextgeoss_get_jira_script': helpers.get_jira_script,
             'nextgeoss_get_add_feedback_url': helpers.get_add_feedback_url,
             'nextgeoss_get_bug_disclaimer': helpers.get_bug_disclaimer,
             'nextgeoss_get_topic_resources': helpers.topic_resources,
             'nextgeoss_get_value': helpers.get_value,
             'nextgeoss_get_pilot_extras': helpers.get_pilot_extras,
             'ng_extra_names': helpers.get_extra_names,
             'ng_extras_to_exclude': helpers.get_extras_to_exclude,
             'ng_get_dataset_thumbnail_path': helpers.get_dataset_thumbnail_path,  # noqa: E501
             'ng_get_source_namespace': helpers.get_source_namespace,
             'nextgeoss_get_site_statistics': helpers.nextgeoss_get_site_statistics,  # noqa: E501
             'get_collections_count': helpers.get_collections_count,
             'get_collection_url': helpers.get_collection_url,
             'get_collections_dataset_count': helpers.get_collections_dataset_count,
             'get_collections_groups': helpers.get_collections_groups,
             'nextgeoss_get_facet_title': helpers.nextgeoss_get_facet_title,
             'get_default_slider_values': helpers.get_default_slider_values,
             'get_date_url_param': helpers.get_date_url_param,
             'get_group_collection_count': helpers.get_group_collection_count,
             'collection_information': helpers.collection_information,
             'get_extras_value': helpers.get_extras_value,
             'generate_opensearch_query': helpers.generate_opensearch_query,
             'get_topics_spatial_information': helpers.get_topics_spatial_information,
             'get_begin_period_topics': helpers.get_begin_period_topics,
             'get_end_period_topics': helpers.get_end_period_topics
        }

    # IRoutes

    def before_map(self, map):
        # Rename organizations
        map.redirect('/organization', '/provider',
                     _redirect_code='301 Moved Permanently')
        map.redirect('/organization/{url}?{qq}', '/provider/{url}{query}',
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
            m.connect('topic_index', '/topic', action='index',
                      highlight_actions='index search')
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
            m.connect('opensearch', '/opensearch',
                      action='opensearch')
            m.connect('collections', '/collection',
                      action='collections')
            m.connect('support', '/support',
                      action='support')

        package_controller = 'ckanext.nextgeoss.controllers.package:NextgeossPackageController'  # noqa: E501
        with routes.mapper.SubMapper(map, controller=package_controller) as m:
          m.connect('search', '/dataset', action='search',
                    highlight_actions='index search')

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
        facets_dict.clear()
        facets_dict['collection_name'] = plugins.toolkit._('Collections')
        facets_dict['groups'] = _('Topics')
        facets_dict['organization'] = _('Providers')
        facets_dict['FamilyName']  = plugins.toolkit._('Family Name')
        facets_dict['ProductType'] = plugins.toolkit._('Product Type')
        facets_dict['OrbitDirection'] = plugins.toolkit._('Orbit Direction')
        facets_dict['Swath'] = plugins.toolkit._('Acquisition Mode')
        facets_dict['TransmitterReceiverPolarisation'] = plugins.toolkit._('Polarisation')

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

    # IPackageController

    def before_index(self, pkg_dict):
        """Expand extras if they're saved as a single string."""
        dataset_extra = pkg_dict.pop("dataset_extra", None)
        if dataset_extra:
            pkg_dict.update(convert_dataset_extra(dataset_extra))
        pkg_dict.pop("extras_dataset_extra", None)

        # Handle spatial indexing here since the string extras break
        # the spatial extension.
        noa = pkg_dict.get("noa_expiration_date", None)

        if noa is not None:
            pkg_dict.pop("noa_expiration_date", None)

        geometry = pkg_dict.get("spatial", None)
        if geometry:
            geometry = json.loads(geometry)
            wkt = None

            # Check potential problems with bboxes
            if geometry['type'] == 'Polygon' \
               and len(geometry['coordinates']) == 1 \
               and len(geometry['coordinates'][0]) == 5:

                # Check wrong bboxes (4 same points)
                xs = [p[0] for p in geometry['coordinates'][0]]
                ys = [p[1] for p in geometry['coordinates'][0]]

                if xs.count(xs[0]) == 5 and ys.count(ys[0]) == 5:
                    wkt = 'POINT({x} {y})'.format(x=xs[0], y=ys[0])
                else:
                    # Check if coordinates are defined counter-clockwise,
                    # otherwise we'll get wrong results from Solr
                    lr = shapely.geometry.polygon.LinearRing(geometry['coordinates'][0])  # noqa: E501
                    if not lr.is_ccw:
                        lr.coords = list(lr.coords)[::-1]
                    polygon = shapely.geometry.polygon.Polygon(lr)
                    wkt = polygon.wkt

            if not wkt:
                shape = shapely.geometry.asShape(geometry)
                if not shape.is_valid:
                    return pkg_dict
                wkt = shape.wkt

            pkg_dict['spatial_geom'] = wkt

        return pkg_dict

    def after_show(self, context, pkg_dict):
        """
        Convert extras saved as a string to a normal extras list
        when a package is requested.
        """
        return string_extras_to_extras_list(pkg_dict)

    def after_search(self, search_results, search_params):
        """
        Convert extras saved as a string to a normal extras list
        for all packages that appear in search results.
        """
        search_results["results"] = [string_extras_to_extras_list(result)
                                     for result in search_results["results"]]

        return search_results


# Make the portal private for the beta
# Yes, this is bad.
# Locking down the beta is worse.
# When the beta is over, we can just delete this section.


def private(self, action, **env):
    if "oauth2" in config.get("ckan.plugins"):
        url = h.current_url()
        if not c.userobj \
            and url != "/user/login" \
            and url != "/user/register" \
            and url != "/private" \
            and not url.startswith("/opensearch") \
            and not url.startswith("/logs") \
            and not url.startswith("/oauth2"):  # noqa: E129

            return h.redirect_to("/private")

        elif not c.userobj \
            or url == "/user/login" \
            or url == "/user/register" \
            or url == "/private" \
            or url.startswith("/opensearch") \
            or url.startswith("/logs") \
            or url.startswith("/oauth2"):  # noqa: E129

            pass

        elif getattr(c.userobj, "about", "false") != "true" \
            and url != "/user/login" \
            and url != "/user/register" \
            and url != "/unauthorized" \
            and not url.startswith("/opensearch") \
            and not url.startswith("/logs") \
            and not url.startswith("/oauth2"):  # noqa: E129

            return h.redirect_to("/unauthorized")
    else:
        pass

# Monkeypatch the controllers so that we can lock down the beta.
base.BaseController.__after__ = private  # noqa: E305

# End of private beta code


def convert_dataset_extra(dataset_extra_string):
    """Convert the dataset_extra string into indexable extras."""
    extras = ast.literal_eval(dataset_extra_string)

    return [(extra["key"], extra["value"]) for extra in extras]


def string_extras_to_extras_list(pkg_dict):
    """Convert extras saved as a string to a normal extras list."""
    extras = pkg_dict.get("extras")

    if extras and extras[0]["key"] == "dataset_extra":
        pkg_dict["extras"] = ast.literal_eval(extras[0]["value"])

    return pkg_dict
