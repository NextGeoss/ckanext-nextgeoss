from collections import OrderedDict

import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as tk

from ckan.common import _, c
from ckanext.opensearch import config as opensearch_config


class StaticController(base.BaseController):

    def __before__(self, action, **env):
        try:
            base.BaseController.__before__(self, action, **env)
            context = {'model': model, 'user': c.user,
                       'auth_user_obj': c.userobj}
            logic.check_access('site_read', context)
        except logic.NotAuthorized:
            base.abort(403, _('Not authorized to see this page'))

    def cookies(self):
        return base.render('static/cookies.html')

    def codeofconduct(self):
        return base.render('static/codeofconduct.html')

    def termsandconditions(self):
        return base.render('static/termsandconditions.html')

    def privacy(self):
        return base.render('static/privacy.html')

    def provide(self):
        return base.render('static/provide.html')

    def use(self):
        return base.render('static/use.html')

    def develop(self):
        return base.render('static/develop.html')

    def private(self):
        return base.render('static/private.html')

    def unauthorized(self):
        return base.render('static/unauthorized.html')

    def opensearch(self):
        return base.render('static/opensearch.html')

    def support(self):
        return tk.redirect_to('https://servicedesk.nextgeoss.eu')

    def collections(self):
        collection_list = opensearch_config.load_settings("collections_list")
        collection_list_newest_first = OrderedDict(reversed(collection_list.items()))
        return base.render('static/collection_list.html',
            extra_vars={'collection_list': collection_list_newest_first})

    def support(self):
        return tk.redirect_to('https://servicedesk.nextgeoss.eu')
