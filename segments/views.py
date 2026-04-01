from rest_framework import viewsets
from .models import Segment
from .serializers import SegmentSerializer # À créer
from marketing.permissions import IsAgent

class SegmentViewSet(viewsets.ModelViewSet):
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer
    permission_classes = [IsAgent]