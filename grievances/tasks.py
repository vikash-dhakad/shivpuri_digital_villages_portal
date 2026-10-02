"""Grievance Celery tasks — matches GrievanceEscalationScheduler.java exactly."""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def escalate_pending_grievances():
    """Escalate grievances that have been PENDING for more than 7 days.
    Matches GrievanceEscalationScheduler.escalatePendingGrievances() — runs every 6 hours.
    """
    from grievances.models import Grievance, GrievanceStatus

    logger.info('Running grievance escalation scheduler...')

    threshold_date = timezone.now() - timedelta(days=7)
    pending_grievances = Grievance.objects.filter(
        status=GrievanceStatus.PENDING,
        created_at__lt=threshold_date,
        escalated=False,
    )

    count = 0
    for grievance in pending_grievances:
        grievance.escalated = True
        grievance.save(update_fields=['escalated'])
        logger.info(f'Escalated Grievance ID: {grievance.id} (Created at: {grievance.created_at})')
        count += 1

    if count:
        logger.info(f'Escalated {count} grievances.')
    else:
        logger.info('No grievances needed escalation.')
