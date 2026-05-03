import pandas as pd
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Max
from django.utils import timezone

from .models import Customer
from .serializers import CustomerSerializer
from .filters import CustomerFilter
from marketing.permissions import IsAgent

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clients avec support d'importation massive,
    statistiques géographiques et suivi d'activité.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAgent]
    
    # Ajout des parsers pour gérer l'upload de fichiers
    parser_classes = [MultiPartParser, FormParser]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CustomerFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'city']
    ordering_fields = ['created_at', 'last_name', 'total_orders']
    

    def get_queryset(self):
        """
        Optimisation : On utilise prefetch_related pour les commandes 
        et on annote le queryset avec la date de la dernière commande.
        """
        return Customer.objects.prefetch_related('orders').annotate(
            last_order_date=Max('orders__created_at')
        ).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def map_stats(self, request):
        """Retourne la répartition des clients par ville pour la carte Leaflet."""
        stats = Customer.objects.values('city').annotate(total=Count('id'))
        data = {item['city']: item['total'] for item in stats if item['city']}
        return Response(data)

    @action(detail=False, methods=['post'], url_path='import-external')
    def import_customers(self, request):
        """
        Action pour importer des clients via un fichier CSV ou Excel.
        Format attendu : first_name, last_name, email, city, phone, gender
        """
        file = request.FILES.get('file')
        print(f"Content-Type reçu : {request.content_type}") # Regardez votre terminal Django
        print(f"Fichiers reçus : {request.FILES}")
        
        if not file:
            return Response(
                {"error": "Veuillez fournir un fichier (CSV ou Excel)."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Lecture du fichier selon l'extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return Response(
                    {"error": "Format de fichier non supporté."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Nettoyage et préparation des données
            df = df.where(pd.notnull(df), None)
            customers_to_create = []
            emails_existing = set(Customer.objects.values_list('email', flat=True))
            
            for _, row in df.iterrows():
                email = str(row.get('email', '')).strip()
                
                # On évite les doublons d'emails durant l'import
                if email and email not in emails_existing:
                    customers_to_create.append(Customer(
                        first_name=row.get('first_name', 'Import'),
                        last_name=row.get('last_name', 'Anonyme'),
                        email=email,
                        phone=row.get('phone'),
                        city=row.get('city', 'Nouakchott'),
                        gender=row.get('gender', 'M'),
                        # Valeur par défaut pour la date de naissance si absente
                        date_of_birth=row.get('date_of_birth', '1990-01-01')
                    ))
                    emails_existing.add(email)

            # Création massive pour la performance
            created = Customer.objects.bulk_create(customers_to_create)
            
            return Response({
                "message": f"Succès : {len(created)} clients importés.",
                "total_rows_processed": len(df)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Erreur lors du traitement : {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )