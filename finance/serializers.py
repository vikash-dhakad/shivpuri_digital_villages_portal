"""Finance serializers matching BudgetResponse.java and ProjectResponse.java."""

from rest_framework import serializers
from finance.models import Budget, Project


class BudgetSerializer(serializers.ModelSerializer):
    villageId = serializers.IntegerField(source='village_id', read_only=True)
    fiscalYear = serializers.CharField(source='fiscal_year')
    totalAmount = serializers.DecimalField(source='total_amount', max_digits=15, decimal_places=2)
    allocatedAmount = serializers.DecimalField(source='allocated_amount', max_digits=15, decimal_places=2)
    spentAmount = serializers.DecimalField(source='spent_amount', max_digits=15, decimal_places=2)
    remainingAmount = serializers.DecimalField(source='remaining_amount', max_digits=15, decimal_places=2, read_only=True)
    unallocatedAmount = serializers.DecimalField(source='unallocated_amount', max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'villageId', 'fiscalYear', 'totalAmount', 'allocatedAmount', 'spentAmount', 'remainingAmount', 'unallocatedAmount']


class ProjectSerializer(serializers.ModelSerializer):
    allocatedBudget = serializers.DecimalField(source='allocated_budget', max_digits=15, decimal_places=2)
    spentAmount = serializers.DecimalField(source='spent_amount', max_digits=15, decimal_places=2)
    villageId = serializers.IntegerField(source='village_id', read_only=True)
    budgetId = serializers.IntegerField(source='budget_id', read_only=True)
    fiscalYear = serializers.CharField(source='budget.fiscal_year', read_only=True)
    documentUrl = serializers.CharField(source='document_url', allow_null=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'status', 'allocatedBudget', 'spentAmount',
                  'villageId', 'budgetId', 'fiscalYear', 'documentUrl']
