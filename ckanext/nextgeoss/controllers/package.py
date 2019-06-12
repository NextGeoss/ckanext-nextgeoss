# encoding: utf-8

import logging
from urllib import urlencode
import datetime

import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
from paste.deploy.converters import asbool

from ckan.controllers.package import PackageController, _encode_params
from ckan.common import c
from ckan.common import OrderedDict, _, json, request, c, response
import ckan.lib.helpers as h
from ckan.common import config
from ckanext.nextgeoss import helpers
import ckan.plugins as p


log = logging.getLogger(__name__)

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def search_url(params, package_type=None):
    if not package_type or package_type == 'dataset':
        url = h.url_for(controller='package', action='search')
    else:
        url = h.url_for('{0}_search'.format(package_type))
    return url_with_params(url, params)


class NextgeossPackageController(PackageController):
    def _to_dt(self, v):
        return '{v}T00:00:00Z'.format(v=v)


    def search(self):
        from ckan.lib.search import SearchError, SearchQueryError

        package_type = self._guess_package_type()

        try:
            context = {'model': model, 'user': c.user,
                       'auth_user_obj': c.userobj}
            check_access('site_read', context)
        except NotAuthorized:
            abort(403, _('Not authorized to see this page'))

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', u'')
        c.query_error = False
        page = h.get_page_number(request.params)

        limit = int(config.get('ckan.datasets_per_page', 20))

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='package', action='search',
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='package', action='search')

        c.remove_field = remove_field

        sort_by = request.params.get('sort', None)
        params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']


        def _sort_by(fields):
            """
            Sort by the given list of fields.

            Each entry in the list is a 2-tuple: (fieldname, sort_order)

            eg - [('metadata_modified', 'desc'), ('name', 'asc')]

            If fields is empty, then the default ordering is used.
            """
            params = params_nosort[:]

            if fields:
                sort_string = ', '.join('%s %s' % f for f in fields)
                params.append(('sort', sort_string))
            return search_url(params, package_type)

        c.sort_by = _sort_by
        if not sort_by:
            c.sort_by_fields = []
        else:
            c.sort_by_fields = [field.split()[0]
                                for field in sort_by.split(',')]

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params, package_type)

        c.search_url_params = urlencode(_encode_params(params_nopage))
        timerange = []
        collection_params = ''

        try:
            c.fields = []
            # c.fields_grouped will contain a dict of params containing
            # a list of values eg {'tags':['tag1', 'tag2']}
            c.fields_grouped = {}
            c.parameters_grouped = {}
            search_extras = {}
            fq = ''
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort', 'timerange_start', 'timerange_end'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                        if param == 'collection_name':
                            collection_params = value
                    else:
                        search_extras[param] = value

                from ckanext.opensearch import converters
                from ckanext.opensearch.config import PARAMETERS

                if param == 'timerange_start':
                    if len(value) > 0:
                        c.parameters_grouped[param] = value
                        for converter in PARAMETERS['collection'][param].get("converters", []):
                            value = getattr(converters, converter)(value)
                        c.fields.append((param, value))
                        fq += " %s:%s" % (param, value)
                        timerange.append(param)

                if param == 'timerange_end':
                    if len(value) > 0:
                        c.parameters_grouped[param] = value
                        for converter in PARAMETERS['collection'][param].get("converters", []):
                            value = getattr(converters, converter)(value)
                        c.fields.append((param, value))
                        fq += " %s:%s" % (param, value)

            context = {'model': model, 'session': model.Session,
                       'user': c.user, 'for_view': True,
                       'auth_user_obj': c.userobj}

            if package_type and package_type != 'dataset':
                # Only show datasets of this particular type
                fq += ' +dataset_type:{type}'.format(type=package_type)
            else:
                # Unless changed via config options, don't show non standard
                # dataset types on the default search page
                if not asbool(
                        config.get('ckan.search.show_all_types', 'False')):
                    fq += ' +dataset_type:dataset'

            facets = OrderedDict()
            search_parameters = OrderedDict()

            default_facet_titles = {
                'collection_name': _('Collections'),
                'organization': _('Organizations'),
                'groups': _('Groups'),
                'tags': _('Tags'),
                'res_format': _('Formats'),
                'license_id': _('Licenses'),
            }

            sentinel_facet_titles = {
                'FamilyName': _('Family Name'),
                'ProductType': _('Product Type'),
                'OrbitDirection': _('Orbit Direction'),
                'Swath': _('Acquisition Mode'),
                'TransmitterReceiverPolarisation': _('Polarisation'),
            }

            default_search_titles = {
                'timerange_start': _('Timerange Start'),
                'timerange_end': _('Timerange End'),
            }

            collection_names = ['Sentinel-1 Level-1 (SLC)', 'Sentinel-1 Level-1 (GRD)', 'Sentinel-1 Level-2 (OCN)',
                    'Sentinel-2 Level-1C', 'Sentinel-2 Level-2A', 'Sentinel-3 SRAL Level-1 SRA']

            for facet in h.facets():
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            for search_param in helpers.search_params():
                if search_param in default_search_titles:
                    search_parameters[search_param] = default_search_titles[search_param]

            # Facet titles
            for plugin in p.PluginImplementations(p.IFacets):
                facets = plugin.dataset_facets(facets, package_type)

            if collection_params not in collection_names:
                for f in facets:
                    if f in sentinel_facet_titles:
                        del facets[f]

            c.facet_titles = facets

            c.search_parameters = search_parameters

            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras,
                'include_private': asbool(config.get(
                'ckan.search.default_include_private', True)),
            }

            query = get_action('package_search')(context, data_dict)
            c.sort_by_selected = query['sort']

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )

            c.search_facets = query['search_facets']
            c.search_search_parameters = search_parameters
            c.page.items = query['results']
        except SearchQueryError, se:
            # User's search parameters are invalid, in such a way that is not
            # achievable with the web interface, so return a proper error to
            # discourage spiders which are the main cause of this.
            log.info('Dataset search query rejected: %r', se.args)
            abort(400, _('Invalid search query: {error_message}')
                  .format(error_message=str(se)))
        except SearchError, se:
            # May be bad input from the user, but may also be more serious like
            # bad code causing a SOLR syntax error, or a problem connecting to
            # SOLR
            log.error('Dataset search error: %r', se.args)
            c.query_error = True
            c.search_facets = {}
            c.page = h.Page(collection=[])
        except NotAuthorized:
            abort(403, _('Not authorized to see this page'))

        c.search_facets_limits = {}
        for facet in c.search_facets.keys():
            try:
                limit = int(request.params.get('_%s_limit' % facet,
                            int(config.get('search.facets.default', 10))))
            except ValueError:
                abort(400, _('Parameter "{parameter_name}" is not '
                             'an integer').format(
                      parameter_name='_%s_limit' % facet))
            c.search_facets_limits[facet] = limit

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        return render(self._search_template(package_type),
                      extra_vars={'dataset_type': package_type})