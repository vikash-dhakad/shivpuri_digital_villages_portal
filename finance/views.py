"""Finance views — matches FinanceController.java + FinanceService.java exactly.
Budget allocation (cumulative) and Project management with budget validation.
"""

import os
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from finance.models import Budget, Project, ProjectStatus
from finance.serializers import BudgetSerializer, ProjectSerializer
from accounts.permissions import IsPanchayatAdmin


# ─── Budget ────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsPanchayatAdmin])
@transaction.atomic
def create_or_update_budget(request):
    """POST /api/finance/budget/ — matches FinanceService.allocateBudget().
    If budget for same village + fiscal year exists, adds to it (cumulative).
    """
    user = request.user
    village = user.village

    if village is None:
        return Response({'error': 'User must be associated with a village'}, status=status.HTTP_400_BAD_REQUEST)

    fiscal_year = request.data.get('fiscalYear', '')
    total_amount = Decimal(str(request.data.get('totalAmount', '0')))

    budget, created = Budget.objects.get_or_create(
        village=village,
        fiscal_year=fiscal_year,
        defaults={'total_amount': total_amount}
    )

    if not created:
        # Cumulative: add to existing budget (same as Spring Boot)
        budget.total_amount += total_amount
        budget.save()

    serializer = BudgetSerializer(budget)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_budget(request, village_id):
    """GET /api/finance/budget/village/<id>/ — get budget for fiscal year or latest.
    Query params: ?fiscalYear=2024-2025 or ?all=true
    """
    fiscal_year = request.query_params.get('fiscalYear', '').strip()
    if request.query_params.get('all') == 'true':
        budgets = Budget.objects.filter(village_id=village_id).order_by('-fiscal_year')
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)

    if fiscal_year:
        try:
            budget = Budget.objects.get(village_id=village_id, fiscal_year=fiscal_year)
            serializer = BudgetSerializer(budget)
            return Response(serializer.data)
        except Budget.DoesNotExist:
            return Response({'error': 'Budget not found for given fiscal year'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Return latest budget for this village
        budget = Budget.objects.filter(village_id=village_id).order_by('-fiscal_year', '-created_at').first()
        if budget:
            serializer = BudgetSerializer(budget)
            return Response(serializer.data)
        return Response({'error': 'No budget found for this village'}, status=status.HTTP_404_NOT_FOUND)


# ─── Projects ──────────────────────────────────────────────────────

def _save_project_file(file, subfolder='project-docs'):
    """Save uploaded project document."""
    if file is None:
        return None
    upload_dir = os.path.join(settings.MEDIA_ROOT, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.name)[1] if file.name else ''
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return f"{settings.MEDIA_URL}{subfolder}/{filename}"


@api_view(['POST'])
@permission_classes([IsPanchayatAdmin])
@transaction.atomic
def create_project(request):
    """POST /api/finance/projects/ — matches FinanceService.addProject().
    Validates allocated budget against unallocated budget.
    """
    user = request.user
    village = user.village

    if village is None:
        return Response({'error': 'User must be associated with a village'}, status=status.HTTP_400_BAD_REQUEST)

    budget_id = request.data.get('budgetId')
    budget = None
    if budget_id:
        try:
            budget = Budget.objects.get(id=budget_id, village=village)
        except Budget.DoesNotExist:
            pass

    if not budget:
        # Fallback to the latest active budget for the village
        budget = Budget.objects.filter(village=village).order_by('-fiscal_year', '-created_at').first()
        if not budget:
            return Response({'error': 'Panchayat Budget not found. Please allocate a budget first.'}, status=status.HTTP_400_BAD_REQUEST)

    allocated_amount = Decimal(str(request.data.get('allocatedBudget', '0') or '0'))
    spent_amount = Decimal(str(request.data.get('spentAmount', '0') or '0'))
    unallocated = budget.unallocated_amount

    if allocated_amount > unallocated:
        return Response(
            {'error': f'Allocated amount (₹{allocated_amount}) exceeds unallocated budget (₹{unallocated})'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update budget allocated amount and spent amount
    budget.allocated_amount += allocated_amount
    if spent_amount > 0:
        budget.spent_amount += spent_amount
        if budget.spent_amount > budget.total_amount:
            return Response(
                {'error': f'Spent amount (₹{spent_amount}) exceeds total budget (₹{budget.total_amount})'},
                status=status.HTTP_400_BAD_REQUEST
            )
    budget.save()

    document = request.FILES.get('document')
    document_url = _save_project_file(document)

    project = Project.objects.create(
        title=request.data.get('title', ''),
        description=request.data.get('description', ''),
        village=village,
        budget=budget,
        allocated_budget=allocated_amount,
        spent_amount=spent_amount,
        document_url=document_url,
    )

    serializer = ProjectSerializer(project)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def village_projects(request, village_id):
    """GET /api/finance/projects/village/<id>/ — list projects."""
    projects = Project.objects.filter(village_id=village_id).select_related('budget')
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsPanchayatAdmin])
@transaction.atomic
def update_project_status(request, pk):
    """PUT /api/finance/projects/<id>/status/ — update project status and/or spent amount."""
    try:
        project = Project.objects.select_related('budget').get(id=pk)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status', '').strip()
    if new_status:
        project.status = new_status

    spent = request.data.get('spentAmount')
    if spent is not None and str(spent).strip() != '':
        spent_decimal = Decimal(str(spent))
        if spent_decimal < 0:
            return Response({'error': 'Kharcha (spent amount) cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)

        old_spent = project.spent_amount
        diff = spent_decimal - old_spent

        # Ensure spent amount does not exceed total budget
        if diff > 0 and (project.budget.spent_amount + diff) > project.budget.total_amount:
            return Response(
                {'error': f'Kharcha (₹{spent_decimal}) total budget (₹{project.budget.total_amount}) se zyada nahi ho sakta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update budget spent amount
        project.budget.spent_amount += diff
        # If spent exceeds allocated budget, adjust allocated accordingly
        if project.budget.spent_amount > project.budget.allocated_amount:
            project.budget.allocated_amount = project.budget.spent_amount
        if spent_decimal > project.allocated_budget:
            project.allocated_budget = spent_decimal

        project.budget.save()
        project.spent_amount = spent_decimal

    project.save()
    serializer = ProjectSerializer(project)
    return Response(serializer.data)
