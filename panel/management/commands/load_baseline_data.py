# panel/management/commands/load_baseline_data.py
import csv
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from panel.models import Respondent


class Command(BaseCommand):
    help = 'Load baseline respondent data from CSV'

    def handle(self, *args, **kwargs):
        csv_path = os.path.join('data', 'baseline_respondents.csv')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(
                f'CSV file not found at {csv_path}'
            ))
            return

        created_count = 0
        skipped_count = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if Respondent.objects.filter(email=row['email']).exists():
                    skipped_count += 1
                    continue

                Respondent.objects.create(
                    name     = row['name'],
                    email    = row['email'],
                    phone    = row['phone'],
                    city     = row['city'],
                    category = row['category'],
                    status   = row['status'],
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created: {created_count} | Skipped: {skipped_count}'
        ))