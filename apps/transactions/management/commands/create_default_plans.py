from django.core.management.base import BaseCommand
from apps.transactions.models import MembershipPlan
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates default membership plans if they do not exist'

    def handle(self, *args, **kwargs):
        # Define default plans
        default_plans = [
            {
                'name': 'Basic Plan',
                'description': 'Basic membership plan with limited borrowing privileges.',
                'duration_days': 30,
                'max_books_allowed': 2,
                'max_borrowing_days': 7,
                'price': 500,
                'is_active': True,
            },
            {
                'name': 'Standard Plan',
                'description': 'Standard membership plan with moderate borrowing privileges.',
                'duration_days': 90,
                'max_books_allowed': 5,
                'max_borrowing_days': 14,
                'price': 1200,
                'is_active': True,
            },
            {
                'name': 'Premium Plan',
                'description': 'Premium membership plan with extensive borrowing privileges.',
                'duration_days': 365,
                'max_books_allowed': 10,
                'max_borrowing_days': 30,
                'price': 3500,
                'is_active': True,
            },
        ]

        # Create plans if they don't exist
        plans_created = 0
        for plan_data in default_plans:
            # Check if a plan with this name already exists
            if not MembershipPlan.objects.filter(name=plan_data['name']).exists():
                MembershipPlan.objects.create(**plan_data)
                plans_created += 1
                self.stdout.write(self.style.SUCCESS(f"Created plan: {plan_data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Plan already exists: {plan_data['name']}"))

        if plans_created > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully created {plans_created} membership plans"))
        else:
            self.stdout.write(self.style.SUCCESS("All default plans already exist"))
