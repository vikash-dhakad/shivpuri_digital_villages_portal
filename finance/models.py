"""Finance models — Budget and Project.
Matches existing Spring Boot entities exactly.
"""

from decimal import Decimal
from django.db import models
from accounts.models import Village


class Budget(models.Model):
    """Budget entity — matches existing Budget.java exactly."""
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='budgets'
    )
    fiscal_year = models.CharField(max_length=20)  # e.g., "2023-2024"
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'
        unique_together = ['village', 'fiscal_year']

    def __str__(self):
        return f"Budget {self.fiscal_year} - {self.village.name}"

    @property
    def remaining_amount(self):
        """Actual remaining balance after project expenditures (Total Budget - Total Spent)."""
        return max(Decimal('0.00'), self.total_amount - self.spent_amount)

    @property
    def unallocated_amount(self):
        """Unallocated funds (Total Budget - Allocated Amount)."""
        return max(Decimal('0.00'), self.total_amount - self.allocated_amount)


class ProjectStatus(models.TextChoices):
    PLANNED = 'PLANNED', 'Planned'
    ONGOING = 'ONGOING', 'Ongoing'
    COMPLETED = 'COMPLETED', 'Completed'


class Project(models.Model):
    """Project entity — matches existing Project.java exactly.
    Note: DB column 'name' maps to field 'title' (same as original).
    """
    title = models.CharField(max_length=255, db_column='name')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices,
        default=ProjectStatus.PLANNED
    )
    allocated_budget = models.DecimalField(
        max_digits=15, decimal_places=2, db_column='allocated_amount'
    )
    spent_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='projects'
    )
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name='projects'
    )
    document_url = models.CharField(max_length=500, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    contractor_name = models.CharField(max_length=255, blank=True, null=True)
    contractor_contact = models.CharField(max_length=255, blank=True, null=True)
    completion_cert_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"
