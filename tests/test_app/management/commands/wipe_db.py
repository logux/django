from django.core.management import BaseCommand

from tests.test_app.models import User


class Command(BaseCommand):
    """ Clean up db before tests """

    def handle(self, *args, **options):
        User.objects.all().delete()
