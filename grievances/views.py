"""Grievance views — matches GrievanceController.java + GrievanceService.java exactly.
Includes full state machine validation logic.
"""

import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from grievances.models import Grievance, GrievanceStatus, Feedback
from grievances.serializers import GrievanceSerializer, FeedbackSerializer
from accounts.permissions import IsPanchayatAdmin, IsVillagerFarmerOrAdmin


def _save_uploaded_file(file):
    """Save uploaded file and return URL path."""
    if file is None:
        return None
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'grievance-photos')
    os.makedirs(upload_dir, exist_ok=True)

    import uuid
    ext = os.path.splitext(file.name)[1] if file.name else ''
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    return f"{settings.MEDIA_URL}grievance-photos/{filename}"


@api_view(['POST'])
@permission_classes([IsVillagerFarmerOrAdmin])
def create_grievance(request):
    """POST /api/grievances/ — matches GrievanceService.createGrievance() exactly."""
    user = request.user
    village = user.village

    if village is None:
        return Response(
            {'error': 'User must be associated with a village to file a grievance'},
            status=status.HTTP_400_BAD_REQUEST
        )

    title = request.data.get('title', '')
    description = request.data.get('description', '')
    category = request.data.get('category', '')
    photo = request.FILES.get('photo')

    photo_url = _save_uploaded_file(photo)

    grievance = Grievance.objects.create(
        title=title,
        description=description,
        category=category,
        user=user,
        village=village,
        photo_url=photo_url,
    )

    serializer = GrievanceSerializer(grievance)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_grievances(request):
    """GET /api/grievances/my/ — matches GrievanceService.getGrievancesForUser()."""
    grievances = Grievance.objects.filter(user=request.user).select_related('user', 'village')
    serializer = GrievanceSerializer(grievances, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsPanchayatAdmin])
def village_grievances(request, village_id):
    """GET /api/grievances/village/<id>/ — matches GrievanceService.getGrievancesForVillage()."""
    grievances = Grievance.objects.filter(village_id=village_id).select_related('user', 'village')
    serializer = GrievanceSerializer(grievances, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsPanchayatAdmin])
def update_status(request, pk):
    """PUT /api/grievances/<id>/status/ — matches GrievanceService.updateStatus() exactly.
    Implements the exact same state machine validation.
    """
    try:
        grievance = Grievance.objects.select_related('user', 'village').get(id=pk)
    except Grievance.DoesNotExist:
        return Response({'error': 'Grievance not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    current_status = grievance.status

    # Strict State Machine Rules for Admin (exact match with Java)
    if new_status == GrievanceStatus.REOPENED:
        return Response(
            {'error': 'Admin cannot reopen a grievance. Only the creator can reopen it.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_transition = False
    if current_status == GrievanceStatus.PENDING:
        if new_status in (GrievanceStatus.IN_PROGRESS, GrievanceStatus.RESOLVED):
            valid_transition = True
    elif current_status == GrievanceStatus.IN_PROGRESS:
        if new_status == GrievanceStatus.RESOLVED:
            valid_transition = True
    elif current_status == GrievanceStatus.REOPENED:
        if new_status in (GrievanceStatus.IN_PROGRESS, GrievanceStatus.RESOLVED):
            valid_transition = True
    elif current_status == GrievanceStatus.RESOLVED:
        return Response(
            {'error': 'Cannot update a resolved grievance. It must be reopened by the user first.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not valid_transition:
        return Response(
            {'error': f'Invalid state transition from {current_status} to {new_status}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    grievance.status = new_status
    grievance.save()

    serializer = GrievanceSerializer(grievance)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsVillagerFarmerOrAdmin])
def reopen_grievance(request, pk):
    """PUT /api/grievances/<id>/reopen/ — matches GrievanceService.reopenGrievance() exactly."""
    try:
        grievance = Grievance.objects.select_related('user', 'village').get(id=pk)
    except Grievance.DoesNotExist:
        return Response({'error': 'Grievance not found'}, status=status.HTTP_404_NOT_FOUND)

    # Only the creator can reopen
    if grievance.user.phone != request.user.phone:
        return Response(
            {'error': 'You can only reopen your own grievance'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Can only reopen if it was marked as RESOLVED
    if grievance.status != GrievanceStatus.RESOLVED:
        return Response(
            {'error': 'Only RESOLVED grievances can be reopened'},
            status=status.HTTP_400_BAD_REQUEST
        )

    grievance.status = GrievanceStatus.REOPENED
    grievance.save()

    serializer = GrievanceSerializer(grievance)
    return Response(serializer.data)


# ─── Feedback Endpoints ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request, pk):
    """POST /api/grievances/<id>/feedback/ — submit feedback on a resolved grievance."""
    try:
        grievance = Grievance.objects.select_related('user', 'village').get(id=pk)
    except Grievance.DoesNotExist:
        return Response({'error': 'Grievance not found'}, status=status.HTTP_404_NOT_FOUND)

    # Only creator (or Panchayat Admin) can submit feedback
    if grievance.user_id != request.user.id and request.user.role != 'PANCHAYAT_ADMIN':
        return Response(
            {'error': 'Aap sirf apni shikayat (grievance) par feedback de sakte hain.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Grievance must be RESOLVED
    if grievance.status != GrievanceStatus.RESOLVED:
        return Response(
            {'error': 'Feedback sirf RESOLVED shikayat par hi diya ja sakta hai.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    problem_title = request.data.get('problem_title', '').strip() or grievance.title
    work_quality = request.data.get('work_quality', 'ACHHA')
    comments = request.data.get('comments', '').strip()
    try:
        rating = int(request.data.get('rating', 5))
    except (ValueError, TypeError):
        rating = 5

    if not comments:
        return Response(
            {'error': 'Feedback comment likhna anivarya hai.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 50 words validation
    word_count = len(comments.split())
    if word_count > 50:
        return Response(
            {'error': f'Feedback 50 words se zyada nahi hona chahiye. (Aapke words: {word_count})'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update or create feedback
    feedback, created = Feedback.objects.update_or_create(
        grievance=grievance,
        defaults={
            'user': request.user,
            'village': grievance.village,
            'problem_title': problem_title,
            'work_quality': work_quality,
            'rating': rating,
            'comments': comments,
        }
    )

    serializer = FeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_feedbacks(request):
    """GET /api/grievances/feedbacks/ — list all feedbacks for village or all."""
    village_id = request.query_params.get('village_id')
    if not village_id and request.user.village_id:
        village_id = request.user.village_id

    if village_id and str(village_id).lower() != 'all':
        feedbacks = Feedback.objects.filter(village_id=village_id).select_related('user', 'grievance')
        if not feedbacks.exists():
            feedbacks = Feedback.objects.all().select_related('user', 'grievance')
    else:
        feedbacks = Feedback.objects.all().select_related('user', 'grievance')

    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)
