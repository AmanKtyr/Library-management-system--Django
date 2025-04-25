from django.db import models
from django.conf import settings
from books.models import BookCopy
from libraries.models import Library
from django.utils import timezone
import uuid

class Transaction(models.Model):
    """Model representing a transaction (borrowing or returning a book)."""
    TRANSACTION_TYPE_CHOICES = (
        ('BORROW', 'Borrow'),
        ('RETURN', 'Return'),
        ('RESERVE', 'Reserve'),
        ('CANCEL_RESERVATION', 'Cancel Reservation'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    )

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='transactions')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    transaction_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    return_date = models.DateTimeField(blank=True, null=True)

    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)
    fine_payment_date = models.DateTimeField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_transactions',
        limit_choices_to={'user_type__in': ['SUPER_ADMIN', 'LIBRARY_ADMIN', 'STAFF']}
    )

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.transaction_id} - {self.book_copy.book.title} - {self.user.email}"

    def is_overdue(self):
        if self.transaction_type == 'BORROW' and self.status == 'COMPLETED' and self.due_date:
            return timezone.now() > self.due_date
        return False

    def calculate_fine(self, fine_rate_per_day=1.00):
        """Calculate fine for overdue books."""
        if self.is_overdue():
            days_overdue = (timezone.now() - self.due_date).days
            return days_overdue * fine_rate_per_day
        return 0.00

class MembershipPlan(models.Model):
    """Model representing a membership plan for library members."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_days = models.PositiveIntegerField()
    max_books_allowed = models.PositiveIntegerField()
    max_borrowing_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Membership(models.Model):
    """Model representing a user's membership in a specific library."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, related_name='memberships')

    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    membership_number = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'library')

    def __str__(self):
        return f"{self.user.email} - {self.library.name} - {self.plan.name}"

    def is_expired(self):
        return timezone.now().date() > self.end_date

    def save(self, *args, **kwargs):
        if not self.membership_number:
            # Generate a unique membership number
            self.membership_number = f"MEM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
