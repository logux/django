# This Throttle class was inspired by DRF: https://www.django-rest-framework.org/

import time
from typing import List, Optional

from django.core.cache import cache as default_cache
from django.http import HttpRequest

from logux import settings


class Throttle:
    """ Rate throttling of requests. """
    cache = default_cache
    key = None

    history: List[float] = []

    def __init__(self):
        self.num_requests = settings.THROTTLE['NUM_REQUESTS']
        self.duration = settings.THROTTLE['DURATION']

    def allow_request(self, request: HttpRequest) -> bool:
        """ Returns True if request allows passing inside, otherwise False """

        self.key = self.get_ident(request)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])

        now = time.time()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return False

        return True

    def remember_bad_auth(self, when: float) -> None:
        """ Put identity + request timestamp into the cache """

        self.history.insert(0, when)
        self.cache.set(self.key, self.history, self.duration)

    @staticmethod
    def get_ident(request: HttpRequest) -> Optional[str]:
        """ Get identity (IP address) of client from request """
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        return ''.join(xff.split()) if xff else remote_addr
