# encoding: utf-8

import logging
import ckan.lib.base as base
import ckan.model as model

from ckan.controllers.group import GroupController
from ckan.common import OrderedDict, c, config, request, _

log = logging.getLogger(__name__)

render = base.render


class NextgeossGroupController(GroupController):
    def _guess_group_type(self, expecting_name=False):
        """
            The base CKAN function gets the group_type from the URL,
            this is a problem in the case when the URL mapping is changed
            and instead of group we use something else.
            That will require overriding the GroupController.

        """
        gt = 'group'

        return gt

    # def read(self, id):
    #     group_type = self._ensure_controller_matches_group_type(id)
    #     context = {'model': model, 'session': model.Session,
    #                'user': c.user}
    #     c.group_dict = self._get_group_dict(id)
    #     group_type = c.group_dict['type']
    #     self._setup_template_variables(context, {'id': id},
    #                                    group_type=group_type)
    #     return render(self._read_template(group_type),
    #                   extra_vars={'group_type': group_type})
    def read(self, id, limit=20):
        group_type = self._ensure_controller_matches_group_type(
            id.split('@')[0])

        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True}
        data_dict = {'id': id, 'type': group_type}

        # unicode format (decoded from utf8)
        c.q = request.params.get('q', '')

        try:
            # Do not query for the group datasets when dictizing, as they will
            # be ignored and get requested on the controller anyway
            data_dict['include_datasets'] = False
            c.group_dict = self._action('group_show')(context, data_dict)
            c.group = context['group']
        except (NotFound, NotAuthorized):
            abort(404, _('Group not found'))

        self._read(id, limit, group_type)
        return render(self._read_template(c.group_dict['type']),
                      extra_vars={'group_type': group_type})