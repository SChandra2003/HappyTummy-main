from django.core.management.base import BaseCommand
from donations.models import SurplusFoodRequest
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes surplus food requests older than 1 hour.'

    def handle(self, *args, **options):
        expiry_time = timezone.now() - timedelta(hours=1)
        expired = SurplusFoodRequest.objects.filter(timestamp__lt=expiry_time, is_picked=False)
        count = expired.count()
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired surplus food requests.'))
