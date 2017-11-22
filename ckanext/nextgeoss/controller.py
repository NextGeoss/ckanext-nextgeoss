import ckan.lib.base as base

class StaticController(base.BaseController):

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
