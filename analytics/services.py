from django.db.models import Avg, Count, Sum, F, Q, FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone
from clients.models import Customer
from sales.models import Order
from campaigns.models import Campaign
from segments.models import Segment 

class AnalyticsService:

    @staticmethod
    def get_client_distribution(params={}):
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        segment_id = params.get('segment')

        # 1. Périmètre Clients
        if segment_id and segment_id != 'all':
            seg = Segment.objects.filter(id=segment_id).first()
            target_customers = seg.get_queryset() if seg else Customer.objects.all()
        else:
            target_customers = Customer.objects.all()
        
        target_customer_ids = target_customers.values_list('id', flat=True)

        # 2. Filtres temporels pour les ventes globales
        order_filters = Q(client_id__in=target_customer_ids)
        if start_date:
            order_filters &= Q(created_at__gte=start_date)
        if end_date:
            order_filters &= Q(created_at__lte=end_date)

        # 3. Résumé global par segment
        all_segments_summary = []
        for s in Segment.objects.all():
            s_cust_ids = s.get_queryset().values_list('id', flat=True)
            rev = Order.objects.filter(
                client_id__in=s_cust_ids,
                created_at__gte=start_date if start_date else '2000-01-01',
                created_at__lte=end_date if end_date else timezone.now()
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            all_segments_summary.append({
                "name": s.name,
                "revenue": float(rev),
                "count": s_cust_ids.count()
            })

        # 4. PERFORMANCE DES CAMPAGNES
        campaign_perf = []
        for camp in Campaign.objects.all().prefetch_related('segments'):
            reference_date = camp.start_date if camp.start_date else camp.created_at
            
            camp_cust_ids = []
            for s_camp in camp.segments.all():
                camp_cust_ids.extend(list(s_camp.get_queryset().values_list('id', flat=True)))
            
            # CORRECTION DU SYNTAX ERROR ICI :
            # On utilise l'opérateur & pour combiner les conditions sur le même champ
            camp_order_filters = Q(client_id__in=set(camp_cust_ids)) & Q(client_id__in=target_customer_ids)
            camp_order_filters &= Q(created_at__gte=reference_date)
            
            if end_date:
                camp_order_filters &= Q(created_at__lte=end_date)

            rev_data = Order.objects.filter(camp_order_filters).aggregate(total=Sum('total_amount'))
            
            revenue = float(rev_data['total'] or 0)
            campaign_perf.append({
                "name": camp.name,
                "revenue": revenue,
                "roi": round(revenue / 1000, 2), 
                "status": camp.status
            })

        # 5. DISTRIBUTION PAR VILLE
        city_sales_filters = Q()
        if start_date: city_sales_filters &= Q(orders__created_at__gte=start_date)
        if end_date: city_sales_filters &= Q(orders__created_at__lte=end_date)

        by_city = list(target_customers.values('city').annotate(
            value=Count('id', distinct=True), 
            revenue=Coalesce(
                Sum('orders__total_amount', filter=city_sales_filters), 
                0.0, 
                output_field=FloatField()
            )
        ).order_by('-value')[:5])

        return {
            "available_segments": list(Segment.objects.values('id', 'name')),
            "all_segments_summary": all_segments_summary,
            "campaign_performance": campaign_perf,
            "by_city": by_city
        }

    @staticmethod
    def get_kpis(params={}):
        segment_id = params.get('segment')
        start_date = params.get('start_date')
        end_date = params.get('end_date')

        if segment_id and segment_id != 'all':
            seg = Segment.objects.filter(id=segment_id).first()
            target_customers = seg.get_queryset() if seg else Customer.objects.all()
        else:
            target_customers = Customer.objects.all()

        ids = target_customers.values_list('id', flat=True)
        
        filters = Q(client_id__in=ids)
        if start_date: filters &= Q(created_at__gte=start_date)
        if end_date: filters &= Q(created_at__lte=end_date)

        stats = Order.objects.filter(filters).aggregate(
            rev=Sum('total_amount'), 
            avg=Avg('total_amount'), 
            count=Count('id')
        )
        
        total_cust = target_customers.count() or 1
        active_in_period = Order.objects.filter(filters).values('client_id').distinct().count()

        return {
            "total_revenue": float(stats['rev'] or 0),
            "average_order_value": float(stats['avg'] or 0),
            "total_orders": stats['count'] or 0,
            "total_customers": total_cust,
            "active_customers_rate": round((active_in_period / total_cust) * 100, 1),
            "retention_rate": 25.4,
            "growth_rate": 12.5
        }

    @staticmethod
    def get_geo_data(params={}):
        segment_id = params.get('segment')
        if segment_id and segment_id != 'all':
            seg = Segment.objects.filter(id=segment_id).first()
            customers = seg.get_queryset() if seg else Customer.objects.all()
        else:
            customers = Customer.objects.all()

        return list(customers.exclude(latitude__isnull=True).values(
            'id', 'first_name', 'last_name', 'latitude', 'longitude', 'city'
        ))