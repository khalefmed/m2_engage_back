import random
from django.core.management.base import BaseCommand
from faker import Faker
from clients.models import Customer
from products.models import Product
from sales.models import Order, OrderItem
from django.utils import timezone

class Command(BaseCommand):
    help = 'Génère des données de test massives'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Nombre de clients à créer')

    def handle(self, *args, **kwargs):
        fake = Faker()
        total = kwargs['total']
        
        self.stdout.write(f"Création de {total} clients...")

        # 1. Création de quelques produits
        categories = ['Électronique', 'Mode', 'Maison', 'Santé']
        products = []
        for _ in range(20):
            p = Product.objects.create(
                name=fake.catch_phrase(),
                category=random.choice(categories),
                price=random.uniform(10, 500),
                is_active=True
            )
            products.append(p)

        # 2. Création des clients en masse (Bulk Create pour la performance)
        customers_to_create = []
        for _ in range(total):
            customers_to_create.append(Customer(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                gender=random.choice(['M', 'F']),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
                country=fake.country(),
                city=fake.city(),
                profession=fake.job(),
                latitude=fake.latitude(),
                longitude=fake.longitude()
            ))
        
        Customer.objects.bulk_create(customers_to_create)
        all_customers = Customer.objects.all()

        # 3. Création de quelques ventes aléatoires
        self.stdout.write("Génération des ventes...")
        for customer in all_customers[:total // 2]: # On donne des achats à la moitié des clients
            order = Order.objects.create(client=customer)
            total_order = 0
            for _ in range(random.randint(1, 3)):
                prod = random.choice(products)
                qty = random.randint(1, 2)
                subtotal = prod.price * qty
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit_price=prod.price,
                    subtotal=subtotal
                )
                total_order += subtotal
            order.total_amount = total_order
            order.save()

        self.stdout.write(self.style.SUCCESS(f"Succès ! {total} clients et leurs ventes créés."))