from django.contrib import admin
from finance.models import Budget, Project

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'village', 'fiscal_year', 'total_amount', 'allocated_amount', 'spent_amount']
    list_filter = ['fiscal_year', 'village']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'allocated_budget', 'spent_amount', 'village']
    list_filter = ['status', 'village']
