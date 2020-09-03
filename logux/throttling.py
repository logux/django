import time

from django.core.cache import cache as default_cache
from django.http import HttpRequest


class Throttle:
    """
    Rate throttling of requests.
    """
    cache = default_cache
    timer = time.time
    key = None
    history = []

    def __init__(self):
        # TODO: move it to settings
        self.num_requests = 3
        self.duration = 1

    def allow_request(self, request: HttpRequest):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """

        self.key = self.get_ident(request)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        # noinspection PyAttributeOutsideInit
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return False
        return self.throttle_success()

    def throttle_success(self):
        """
        Inserts the current request's timestamp along with the key
        into the cache.
        """
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True

    @staticmethod
    def get_ident(request: HttpRequest):
        """ Get identity (IP address) of client from request """
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        return ''.join(xff.split()) if xff else remote_addr
