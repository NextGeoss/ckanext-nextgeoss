import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model

from ckan.common import _, c


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
