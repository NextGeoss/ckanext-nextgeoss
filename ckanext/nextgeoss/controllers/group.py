# encoding: utf-8

import logging

import ckan.lib.base as base
import ckan.model as model

from ckan.controllers.group import GroupController
from ckan.common import c

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

    def read(self, id):
        group_type = self._ensure_controller_matches_group_type(id)
        context = {'model': model, 'session': model.Session,
                   'user': c.user}
        c.group_dict = self._get_group_dict(id)
        group_type = c.group_dict['type']
        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)
        return render(self._about_template(group_type),
                      extra_vars={'group_type': group_type})
