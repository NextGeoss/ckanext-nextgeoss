# -*- coding: utf-8 -
import logging
import os

import ckan.lib.helpers as lib_helpers
import ckan.logic as l
import ckan.plugins.toolkit as t
import ckan.model as m

log = logging.getLogger(__name__)

@l.side_effect_free
def get_parent_group(context, data_dict):
    parents = context['model'].Group.get(data_dict['child_id']).get_parent_groups(type=data_dict['type'])
    parents = [p.as_dict() for p in parents]

	return parents[0]