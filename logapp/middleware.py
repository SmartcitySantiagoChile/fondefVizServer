from django.utils import timezone

from logapp.models import UserActions
import logging

logger = logging.getLogger(__name__)


class UserLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = timezone.now()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        end_time = timezone.now()

        if request.user.is_authenticated():
            try:
                UserActions.objects.create(user=request.user, url=request.get_full_path(), method=request.method,
                                           duration=(end_time - start_time))
            except Exception as e:
                logging.error(e)

        return response
