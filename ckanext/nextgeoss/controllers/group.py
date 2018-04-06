# encoding: utf-8

import logging

from ckan.controllers.group import GroupController

log = logging.getLogger(__name__)


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
