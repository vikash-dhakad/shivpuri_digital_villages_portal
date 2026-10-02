"""Village views — matches VillageController.java exactly."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import Village
from accounts.permissions import IsPanchayatAdmin
from accounts.serializers import VillageSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def village_list_create(request):
    """GET /api/villages/ — list all villages (public)
       POST /api/villages/ — add village (PANCHAYAT_ADMIN only)
    """
    if request.method == 'GET':
        villages = Village.objects.all()
        serializer = VillageSerializer(villages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check admin permission for POST
        if not request.user.is_authenticated or request.user.role != 'PANCHAYAT_ADMIN':
            return Response(
                {'error': 'Only Panchayat Admin can add villages'},
                status=status.HTTP_403_FORBIDDEN
            )
        village = Village.objects.create(
            name=request.data.get('name', ''),
            district=request.data.get('district', ''),
            state=request.data.get('state', ''),
            block=request.data.get('block', ''),
            pincode=request.data.get('pincode', ''),
        )
        serializer = VillageSerializer(village)
        return Response(serializer.data)
