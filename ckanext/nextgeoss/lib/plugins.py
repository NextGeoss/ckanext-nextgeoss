# encoding: utf-8

import logging
import os
import sys

from ckan.common import c
from ckan.lib import base
from ckan import logic
import logic.schema
from ckan import plugins
import ckan.authz
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

# Mapping from package-type strings to IDatasetForm instances
_package_plugins = {}
# The fallback behaviour
_default_package_plugin = None

# Mapping from group-type strings to IGroupForm instances
_group_plugins = {}
# The fallback behaviour
_default_group_plugin = None
# Mapping from group-type strings to controllers
_group_controllers = {}


def register_group_plugins(map):
    """
    Register the various IGroupForm instances.

    This method will setup the mappings between group types and the
    registered IGroupForm instances. If it's called more than once an
    exception will be raised.
    """
    global _default_group_plugin

    # This function should have not effect if called more than once.
    # This should not occur in normal deployment, but it may happen when
    # running unit tests.
    if _default_group_plugin is not None:
        return

    # Create the mappings and register the fallback behaviour if one is found.
    for plugin in plugins.PluginImplementations(plugins.IGroupForm):
        if plugin.is_fallback():
            if _default_group_plugin is not None:
                raise ValueError("More than one fallback IGroupForm has been "
                                 "registered")
            _default_group_plugin = plugin

        # Get group_controller from plugin if there is one,
        # otherwise use 'group'
        try:
            group_controller = plugin.group_controller()
        except AttributeError:
            group_controller = 'group'

        for group_type in plugin.group_types():
            # Create the routes based on group_type here, this will
            # allow us to have top level objects that are actually
            # Groups, but first we need to make sure we are not
            # clobbering an existing domain

            # Our version of routes doesn't allow the environ to be
            # passed into the match call and so we have to set it on the
            # map instead. This looks like a threading problem waiting
            # to happen but it is executed sequentially from inside the
            # routing setup

            map.connect('%s_index' % group_type, '/%s' % group_type,
                        controller=group_controller, action='index')
            map.connect('%s_new' % group_type, '/%s/new' % group_type,
                        controller=group_controller, action='new')
            map.connect('%s_read' % group_type, '/%s/{id}' % group_type,
                        controller=group_controller, action='read')
            map.connect('%s_action' % group_type,
                        '/%s/{action}/{id}' % group_type,
                        controller=group_controller,
                        requirements=dict(action='|'.join(
                            ['edit', 'authz', 'delete', 'history', 'member_new',
                             'member_delete', 'followers', 'follow',
                             'unfollow', 'admins', 'activity'])))
            map.connect('%s_edit' % group_type, '/%s/edit/{id}' % group_type,
                        controller=group_controller, action='edit',
                        ckan_icon='pencil-square-o')
            map.connect('%s_members' % group_type,
                        '/%s/members/{id}' % group_type,
                        controller=group_controller,
                        action='members',
                        ckan_icon='users')
            map.connect('%s_activity' % group_type,
                        '/%s/activity/{id}/{offset}' % group_type,
                        controller=group_controller,
                        action='activity', ckan_icon='clock-o'),
            map.connect('%s_about' % group_type, '/%s/about/{id}' % group_type,
                        controller=group_controller,
                        action='about', ckan_icon='info-circle')
            map.connect('%s_bulk_process' % group_type,
                        '/%s/bulk_process/{id}' % group_type,
                        controller=group_controller,
                        action='bulk_process', ckan_icon='sitemap')
            map.connect('%s_output_data' % group_type, '/%s' % group_type,
                        controller=group_controller, action='output_data')

            if group_type in _group_plugins:
                raise ValueError("An existing IGroupForm is "
                                 "already associated with the group type "
                                 "'%s'" % group_type)
            _group_plugins[group_type] = plugin
            _group_controllers[group_type] = group_controller

            controller_obj = None
            # If using one of the default controllers, tell it that it is allowed
            # to handle other group_types.
            # Import them here to avoid circular imports.
            if group_controller == 'group':
                from ckan.controllers.group import GroupController as controller_obj
            elif group_controller == 'organization':
                from ckan.controllers.organization import OrganizationController as controller_obj
            if controller_obj is not None:
                controller_obj.add_group_type(group_type)

    # Setup the fallback behaviour if one hasn't been defined.
    if _default_group_plugin is None:
        _default_group_plugin = DefaultGroupForm()
    if 'group' not in _group_controllers:
        _group_controllers['group'] = 'group'
    if 'organization' not in _group_controllers:
        _group_controllers['organization'] = 'organization'


class DefaultGroupForm(object):
    """
    Provides a default implementation of the pluggable Group controller
    behaviour.

    This class has 2 purposes:

     - it provides a base class for IGroupForm implementations to use if
       only a subset of the method hooks need to be customised.

     - it provides the fallback behaviour if no plugin is setup to
       provide the fallback behaviour.

    Note - this isn't a plugin implementation. This is deliberate, as we
           don't want this being registered.
    """
    def group_controller(self):
        return 'group'

    def new_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the 'new' page
        """
        return 'group/new.html'

    def index_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the index page
        """
        return 'group/index.html'

    def read_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the read page
        """
        return 'group/read.html'

    def about_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the about page
        """
        return 'group/about.html'

    def history_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the history page
        """
        return 'group/history.html'

    def edit_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the edit page
        """
        return 'group/edit.html'

    def activity_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the activity stream page
        """
        return 'group/activity_stream.html'

    def admins_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the admins page
        """
        return 'group/admins.html'

    def bulk_process_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the bulk_process page
        """
        return 'group/bulk_process.html'

    def output_data_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the admins page
        """
        return 'group/output.html'

    def group_form(self):
        return 'group/new_group_form.html'

    def form_to_db_schema_options(self, options):
        ''' This allows us to select different schemas for different
        purpose eg via the web interface or via the api or creation vs
        updating. It is optional and if not available form_to_db_schema
        should be used.
        If a context is provided, and it contains a schema, it will be
        returned.
        '''
        schema = options.get('context', {}).get('schema', None)
        if schema:
            return schema

        if options.get('api'):
            if options.get('type') == 'create':
                return self.form_to_db_schema_api_create()
            else:
                return self.form_to_db_schema_api_update()
        else:
            return self.form_to_db_schema()

    def form_to_db_schema_api_create(self):
        return logic.schema.default_group_schema()

    def form_to_db_schema_api_update(self):
        return logic.schema.default_update_group_schema()

    def form_to_db_schema(self):
        return logic.schema.group_form_schema()

    def db_to_form_schema(self):
        '''This is an interface to manipulate data from the database
        into a format suitable for the form (optional)'''

    def db_to_form_schema_options(self, options):
        '''This allows the selection of different schemas for different
        purposes.  It is optional and if not available, ``db_to_form_schema``
        should be used.
        If a context is provided, and it contains a schema, it will be
        returned.
        '''
        schema = options.get('context', {}).get('schema', None)
        if schema:
            return schema
        return self.db_to_form_schema()

    def check_data_dict(self, data_dict):
        '''Check if the return data is correct, mostly for checking out
        if spammers are submitting only part of the form

        # Resources might not exist yet (eg. Add Dataset)
        surplus_keys_schema = ['__extras', '__junk', 'state', 'groups',
                               'extras_validation', 'save', 'return_to',
                               'resources']

        schema_keys = form_to_db_package_schema().keys()
        keys_in_schema = set(schema_keys) - set(surplus_keys_schema)

        missing_keys = keys_in_schema - set(data_dict.keys())

        if missing_keys:
            #print data_dict
            #print missing_keys
            log.info('incorrect form fields posted')
            raise DataError(data_dict)
        '''
        pass

    def setup_template_variables(self, context, data_dict):
        c.is_sysadmin = ckan.authz.is_sysadmin(c.user)

        ## This is messy as auths take domain object not data_dict
        context_group = context.get('group', None)
        group = context_group or c.group
        if group:
            try:
                if not context_group:
                    context['group'] = group
                logic.check_access('group_change_state', context)
                c.auth_for_change_state = True
            except logic.NotAuthorized:
                c.auth_for_change_state = False