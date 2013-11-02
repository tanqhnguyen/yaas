class UserLanguageMiddleware():
    def process_request(self, request):
        if request.user.is_authenticated():
            request.session['django_language'] = request.user.language
        return None