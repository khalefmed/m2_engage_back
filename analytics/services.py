from django.db.models import Avg, Count, Sum, F, Case, When, Value, CharField
from django.db.models.functions import TruncMonth, ExtractHour
from django.utils import timezone
from datetime import timedelta
from clients.models import Customer
from sales.models import Order, OrderItem

class AnalyticsService:
    @staticmethod
    def get_client_distribution():
        # 1. Sales Trend (On s'assure que 'period' est une chaîne lisible par le JS)
        six_months_ago = timezone.now() - timedelta(days=180)
        trend_query = (
            Order.objects.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )
        # Transformation en liste d'objets simples pour le graphique
        sales_trend = [{"period": item['month'].strftime('%b'), "value": item['total']} for item in trend_query]

        # 2. Revenu par Catégorie (Correction du "DIVERS")
        # On utilise Case/When pour remplacer les catégories vides par "Inconnu"
        cat_perf = OrderItem.objects.annotate(
            cat_name=Case(
                When(product__category__isnull=True, then=Value('Non classé')),
                When(product__category='', then=Value('Non classé')),
                default=F('product__category'),
                output_field=CharField(),
            )
        ).values('cat_name').annotate(
            revenue=Sum('subtotal'),
            units=Sum('quantity')
        ).order_by('-revenue')[:5]

        # Formatage pour React (on renomme cat_name en product__category pour ton code actuel)
        formatted_cat = [
            {"product__category": item['cat_name'], "revenue": float(item['revenue'] or 0), "units": item['units']} 
            for item in cat_perf
        ]

        # 3. Heures d'activité (Remplit enfin le graphique horaire)
        hours_query = Order.objects.annotate(h=ExtractHour('created_at')) \
                         .values('h') \
                         .annotate(count=Count('id')) \
                         .order_by('h')
        
        # On s'assure que TOUTES les heures sont présentes (0 à 23) pour éviter les trous dans le graphique
        peak_hours = []
        hours_dict = {item['h']: item['count'] for item in hours_query}
        for i in range(24):
            peak_hours.append({"hour": i, "count": hours_dict.get(i, 0)})

        # 4. Segmentation (État de la base)
        total = Customer.objects.count() or 1 # Éviter division par zéro
        loyal = Customer.objects.annotate(n=Count('orders')).filter(n__gte=3).count()
        risk_date = timezone.now() - timedelta(days=60)
        at_risk = Customer.objects.filter(orders__created_at__lt=risk_date).distinct().count()

        return {
            "sales_trend": sales_trend,
            "category_performance": formatted_cat,
            "peak_shopping_hours": peak_hours,
            "customer_segments": [
                {"segment": "Fidèles", "percentage": round((loyal/total)*100, 1)},
                {"segment": "À Risque", "percentage": round((at_risk/total)*100, 1)},
                {"segment": "Nouveaux / Autres", "percentage": round(((total - loyal - at_risk)/total)*100, 1)},
            ],
            "by_city": list(Customer.objects.values('city').annotate(value=Count('id'), revenue=Sum('orders__total_amount')).order_by('-revenue')[:5])
        }

    @staticmethod
    def get_kpis():
        total_cust = Customer.objects.count() or 1
        stats = Order.objects.aggregate(rev=Sum('total_amount'), avg=Avg('total_amount'), count=Count('id'))
        
        # Calcul des taux
        active_date = timezone.now() - timedelta(days=30)
        active_count = Customer.objects.filter(orders__created_at__gte=active_date).distinct().count()
        repeat_count = Customer.objects.annotate(n=Count('orders')).filter(n__gt=1).count()

        return {
            "total_revenue": float(stats['rev'] or 0),
            "average_order_value": float(stats['avg'] or 0),
            "total_orders": stats['count'] or 0,
            "total_customers": total_cust,
            "active_customers_rate": round((active_count/total_cust)*100, 1),
            "retention_rate": round((repeat_count/total_cust)*100, 1),
            "growth_rate": 5.4 
        }