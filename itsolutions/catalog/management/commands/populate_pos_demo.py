from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
from catalog.models import POSCategory, POSProduct, POSCustomer, POSSale, POSSaleItem


class Command(BaseCommand):
    help = 'Populate POS demo data'

    def handle(self, *args, **options):
        self.stdout.write('Populating POS demo data...')
        
        # Create POS Categories for different modes
        categories_data = [
            # Restaurant categories
            {
                'name': 'Main Courses',
                'slug': 'main-courses',
                'icon': 'bi-egg-fried',
                'description': 'Main dishes and entrees',
                'order': 1,
                'mode': 'restaurant'
            },
            {
                'name': 'Appetizers',
                'slug': 'appetizers',
                'icon': 'bi-basket',
                'description': 'Starters and appetizers',
                'order': 2,
                'mode': 'restaurant'
            },
            {
                'name': 'Beverages',
                'slug': 'beverages',
                'icon': 'bi-cup-fill',
                'description': 'Drinks and refreshments',
                'order': 3,
                'mode': 'restaurant'
            },
            # Club categories
            {
                'name': 'Cocktails',
                'slug': 'cocktails',
                'icon': 'bi-cup-straw',
                'description': 'Mixed drinks and cocktails',
                'order': 1,
                'mode': 'club'
            },
            {
                'name': 'Beers',
                'slug': 'beers',
                'icon': 'bi-beer-bottle',
                'description': 'Draft and bottled beers',
                'order': 2,
                'mode': 'club'
            },
            {
                'name': 'Spirits',
                'slug': 'spirits',
                'icon': 'bi-bottle',
                'description': 'Hard liquors and spirits',
                'order': 3,
                'mode': 'club'
            },
            # Supermarket categories
            {
                'name': 'Groceries',
                'slug': 'groceries',
                'icon': 'bi-cart-check',
                'description': 'Food and household items',
                'order': 1,
                'mode': 'supermarket'
            },
            {
                'name': 'Dairy',
                'slug': 'dairy',
                'icon': 'bi-cup-hot',
                'description': 'Milk, cheese, and dairy products',
                'order': 2,
                'mode': 'supermarket'
            },
            {
                'name': 'Bakery',
                'slug': 'bakery',
                'icon': 'bi-bread-slice',
                'description': 'Bread and baked goods',
                'order': 3,
                'mode': 'supermarket'
            },
            # Coffee shop categories
            {
                'name': 'Coffee',
                'slug': 'coffee',
                'icon': 'bi-cup-hot-fill',
                'description': 'Hot and cold coffee drinks',
                'order': 1,
                'mode': 'coffeeshop'
            },
            {
                'name': 'Pastries',
                'slug': 'pastries',
                'icon': 'bi-cookie',
                'description': 'Cakes, cookies, and pastries',
                'order': 2,
                'mode': 'coffeeshop'
            },
            {
                'name': 'Tea',
                'slug': 'tea',
                'icon': 'bi-cup',
                'description': 'Various tea selections',
                'order': 3,
                'mode': 'coffeeshop'
            },
            # Cafe categories
            {
                'name': 'Light Meals',
                'slug': 'light-meals',
                'icon': 'bi-sandwich',
                'description': 'Sandwiches and light food',
                'order': 1,
                'mode': 'cafe'
            },
            {
                'name': 'Desserts',
                'slug': 'desserts',
                'icon': 'bi-cake',
                'description': 'Sweet treats and desserts',
                'order': 2,
                'mode': 'cafe'
            },
            {
                'name': 'Smoothies',
                'slug': 'smoothies',
                'icon': 'bi-droplet',
                'description': 'Fresh fruit smoothies',
                'order': 3,
                'mode': 'cafe'
            }
        ]
        
        for cat_data in categories_data:
            category, created = POSCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Get categories
        main_courses_cat = POSCategory.objects.get(slug='main-courses')
        appetizers_cat = POSCategory.objects.get(slug='appetizers')
        beverages_cat = POSCategory.objects.get(slug='beverages')
        cocktails_cat = POSCategory.objects.get(slug='cocktails')
        beers_cat = POSCategory.objects.get(slug='beers')
        spirits_cat = POSCategory.objects.get(slug='spirits')
        groceries_cat = POSCategory.objects.get(slug='groceries')
        dairy_cat = POSCategory.objects.get(slug='dairy')
        bakery_cat = POSCategory.objects.get(slug='bakery')
        coffee_cat = POSCategory.objects.get(slug='coffee')
        pastries_cat = POSCategory.objects.get(slug='pastries')
        tea_cat = POSCategory.objects.get(slug='tea')
        light_meals_cat = POSCategory.objects.get(slug='light-meals')
        desserts_cat = POSCategory.objects.get(slug='desserts')
        smoothies_cat = POSCategory.objects.get(slug='smoothies')
        
        # Create POS Products for different modes
        products_data = [
            # Restaurant products
            {
                'name': 'Grilled Chicken',
                'sku': 'RES-001',
                'category': main_courses_cat,
                'price': Decimal('850.00'),
                'icon': 'bi-egg-fried',
                'image': 'https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=400&h=400&fit=crop',
                'description': 'Grilled chicken with vegetables',
                'stock_quantity': 50,
                'order': 1
            },
            {
                'name': 'Beef Steak',
                'sku': 'RES-002',
                'category': main_courses_cat,
                'price': Decimal('1200.00'),
                'icon': 'bi-fire',
                'image': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400&h=400&fit=crop',
                'description': 'Premium beef steak with sauce',
                'stock_quantity': 30,
                'order': 2
            },
            {
                'name': 'Fish Fillet',
                'sku': 'RES-003',
                'category': main_courses_cat,
                'price': Decimal('950.00'),
                'icon': 'bi-fish',
                'image': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=400&fit=crop',
                'description': 'Grilled fish fillet with lemon',
                'stock_quantity': 40,
                'order': 3
            },
            {
                'name': 'Spring Rolls',
                'sku': 'RES-004',
                'category': appetizers_cat,
                'price': Decimal('350.00'),
                'icon': 'bi-basket',
                'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=400&fit=crop',
                'description': 'Crispy vegetable spring rolls',
                'stock_quantity': 60,
                'order': 4
            },
            {
                'name': 'Garlic Bread',
                'sku': 'RES-005',
                'category': appetizers_cat,
                'price': Decimal('250.00'),
                'icon': 'bi-bread-slice',
                'image': 'https://images.unsplash.com/photo-1619515860434-ba1d8fa12536?w=400&h=400&fit=crop',
                'description': 'Toasted garlic bread with herbs',
                'stock_quantity': 80,
                'order': 5
            },
            {
                'name': 'Fresh Juice',
                'sku': 'RES-006',
                'category': beverages_cat,
                'price': Decimal('200.00'),
                'icon': 'bi-cup-fill',
                'image': 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=400&h=400&fit=crop',
                'description': 'Fresh fruit juice blend',
                'stock_quantity': 100,
                'order': 6
            },
            {
                'name': 'Soft Drink',
                'sku': 'RES-007',
                'category': beverages_cat,
                'price': Decimal('150.00'),
                'icon': 'bi-cup-straw',
                'image': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&h=400&fit=crop',
                'description': 'Chilled soft drink',
                'stock_quantity': 150,
                'order': 7
            },
            # Club products
            {
                'name': 'Mojito',
                'sku': 'CLB-001',
                'category': cocktails_cat,
                'price': Decimal('600.00'),
                'icon': 'bi-cup-straw',
                'image': 'https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400&h=400&fit=crop',
                'description': 'Classic mojito with mint',
                'stock_quantity': 100,
                'order': 8
            },
            {
                'name': 'Margarita',
                'sku': 'CLB-002',
                'category': cocktails_cat,
                'price': Decimal('650.00'),
                'icon': 'bi-cup',
                'image': 'https://images.unsplash.com/photo-1575023782549-62ca0d244b39?w=400&h=400&fit=crop',
                'description': 'Frozen margarita',
                'stock_quantity': 80,
                'order': 9
            },
            {
                'name': 'Draft Beer',
                'sku': 'CLB-003',
                'category': beers_cat,
                'price': Decimal('400.00'),
                'icon': 'bi-beer-bottle',
                'image': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400&h=400&fit=crop',
                'description': 'Fresh draft beer pint',
                'stock_quantity': 200,
                'order': 10
            },
            {
                'name': 'Bottled Beer',
                'sku': 'CLB-004',
                'category': beers_cat,
                'price': Decimal('350.00'),
                'icon': 'bi-beer-bottle-fill',
                'image': 'https://images.unsplash.com/photo-1566633806327-68e152aaf26d?w=400&h=400&fit=crop',
                'description': 'Premium bottled beer',
                'stock_quantity': 150,
                'order': 11
            },
            {
                'name': 'Whiskey',
                'sku': 'CLB-005',
                'category': spirits_cat,
                'price': Decimal('800.00'),
                'icon': 'bi-bottle',
                'image': 'https://images.unsplash.com/photo-1527281400683-1aae777175f8?w=400&h=400&fit=crop',
                'description': 'Premium whiskey shot',
                'stock_quantity': 60,
                'order': 12
            },
            {
                'name': 'Vodka',
                'sku': 'CLB-006',
                'category': spirits_cat,
                'price': Decimal('700.00'),
                'icon': 'bi-bottle-fill',
                'image': 'https://images.unsplash.com/photo-1606787366850-de6330128bfc?w=400&h=400&fit=crop',
                'description': 'Premium vodka shot',
                'stock_quantity': 60,
                'order': 13
            },
            # Supermarket products
            {
                'name': 'Rice (1kg)',
                'sku': 'SUP-001',
                'category': groceries_cat,
                'price': Decimal('180.00'),
                'icon': 'bi-cart-check',
                'image': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=400&fit=crop',
                'description': 'Premium rice 1kg pack',
                'stock_quantity': 200,
                'order': 14
            },
            {
                'name': 'Cooking Oil (1L)',
                'sku': 'SUP-002',
                'category': groceries_cat,
                'price': Decimal('350.00'),
                'icon': 'bi-droplet',
                'image': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=400&fit=crop',
                'description': 'Cooking oil 1 liter',
                'stock_quantity': 150,
                'order': 15
            },
            {
                'name': 'Fresh Milk (500ml)',
                'sku': 'SUP-003',
                'category': dairy_cat,
                'price': Decimal('120.00'),
                'icon': 'bi-cup-hot',
                'image': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=400&fit=crop',
                'description': 'Fresh milk 500ml',
                'stock_quantity': 100,
                'order': 16
            },
            {
                'name': 'Cheese (200g)',
                'sku': 'SUP-004',
                'category': dairy_cat,
                'price': Decimal('250.00'),
                'icon': 'bi-cheese',
                'image': 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400&h=400&fit=crop',
                'description': 'Cheddar cheese 200g',
                'stock_quantity': 80,
                'order': 17
            },
            {
                'name': 'White Bread',
                'sku': 'SUP-005',
                'category': bakery_cat,
                'price': Decimal('80.00'),
                'icon': 'bi-bread-slice',
                'image': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop',
                'description': 'Fresh white bread loaf',
                'stock_quantity': 120,
                'order': 18
            },
            {
                'name': 'Croissants (pack)',
                'sku': 'SUP-006',
                'category': bakery_cat,
                'price': Decimal('150.00'),
                'icon': 'bi-cookie',
                'image': 'https://images.unsplash.com/photo-1555507036-ab1f4038808d?w=400&h=400&fit=crop',
                'description': 'Butter croissants pack of 4',
                'stock_quantity': 60,
                'order': 19
            },
            # Coffee shop products
            {
                'name': 'Espresso',
                'sku': 'COF-001',
                'category': coffee_cat,
                'price': Decimal('200.00'),
                'icon': 'bi-cup-hot-fill',
                'image': 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=400&h=400&fit=crop',
                'description': 'Single shot espresso',
                'stock_quantity': 200,
                'order': 20
            },
            {
                'name': 'Cappuccino',
                'sku': 'COF-002',
                'category': coffee_cat,
                'price': Decimal('350.00'),
                'icon': 'bi-cup-hot',
                'image': 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400&h=400&fit=crop',
                'description': 'Classic cappuccino',
                'stock_quantity': 150,
                'order': 21
            },
            {
                'name': 'Latte',
                'sku': 'COF-003',
                'category': coffee_cat,
                'price': Decimal('380.00'),
                'icon': 'bi-cup-fill',
                'image': 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=400&fit=crop',
                'description': 'Creamy latte',
                'stock_quantity': 150,
                'order': 22
            },
            {
                'name': 'Chocolate Cake',
                'sku': 'COF-004',
                'category': pastries_cat,
                'price': Decimal('450.00'),
                'icon': 'bi-cake',
                'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=400&fit=crop',
                'description': 'Rich chocolate cake slice',
                'stock_quantity': 50,
                'order': 23
            },
            {
                'name': 'Blueberry Muffin',
                'sku': 'COF-005',
                'category': pastries_cat,
                'price': Decimal('180.00'),
                'icon': 'bi-cookie',
                'image': 'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=400&h=400&fit=crop',
                'description': 'Fresh blueberry muffin',
                'stock_quantity': 80,
                'order': 24
            },
            {
                'name': 'Green Tea',
                'sku': 'COF-006',
                'category': tea_cat,
                'price': Decimal('250.00'),
                'icon': 'bi-cup',
                'image': 'https://images.unsplash.com/photo-1556881286-fc6915169721?w=400&h=400&fit=crop',
                'description': 'Premium green tea',
                'stock_quantity': 100,
                'order': 25
            },
            {
                'name': 'Earl Grey',
                'sku': 'COF-007',
                'category': tea_cat,
                'price': Decimal('280.00'),
                'icon': 'bi-cup-fill',
                'image': 'https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?w=400&h=400&fit=crop',
                'description': 'Classic Earl Grey tea',
                'stock_quantity': 100,
                'order': 26
            },
            # Cafe products
            {
                'name': 'Club Sandwich',
                'sku': 'CAF-001',
                'category': light_meals_cat,
                'price': Decimal('550.00'),
                'icon': 'bi-sandwich',
                'image': 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&h=400&fit=crop',
                'description': 'Classic club sandwich',
                'stock_quantity': 60,
                'order': 27
            },
            {
                'name': 'Caesar Salad',
                'sku': 'CAF-002',
                'category': light_meals_cat,
                'price': Decimal('480.00'),
                'icon': 'bi-basket',
                'image': 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400&h=400&fit=crop',
                'description': 'Fresh Caesar salad',
                'stock_quantity': 50,
                'order': 28
            },
            {
                'name': 'Tiramisu',
                'sku': 'CAF-003',
                'category': desserts_cat,
                'price': Decimal('420.00'),
                'icon': 'bi-cake',
                'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400&h=400&fit=crop',
                'description': 'Classic Italian tiramisu',
                'stock_quantity': 40,
                'order': 29
            },
            {
                'name': 'Cheesecake',
                'sku': 'CAF-004',
                'category': desserts_cat,
                'price': Decimal('380.00'),
                'icon': 'bi-pie-chart',
                'image': 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=400&h=400&fit=crop',
                'description': 'New York cheesecake',
                'stock_quantity': 45,
                'order': 30
            },
            {
                'name': 'Mango Smoothie',
                'sku': 'CAF-005',
                'category': smoothies_cat,
                'price': Decimal('320.00'),
                'icon': 'bi-droplet',
                'image': 'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400&h=400&fit=crop',
                'description': 'Fresh mango smoothie',
                'stock_quantity': 80,
                'order': 31
            },
            {
                'name': 'Berry Blast',
                'sku': 'CAF-006',
                'category': smoothies_cat,
                'price': Decimal('350.00'),
                'icon': 'bi-droplet-fill',
                'image': 'https://images.unsplash.com/photo-1553530666-ba11a9068851?w=400&h=400&fit=crop',
                'description': 'Mixed berry smoothie',
                'stock_quantity': 80,
                'order': 32
            }
        ]
        
        for prod_data in products_data:
            product, created = POSProduct.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                # Update existing product with new data including image
                for field, value in prod_data.items():
                    setattr(product, field, value)
                product.save()
                self.stdout.write(f'Updated product: {product.name}')
        
        # Create POS Customers
        customers_data = [
            {
                'name': 'John Kamau',
                'email': 'john@email.com',
                'phone': '0722-123456',
                'total_orders': 5,
                'total_spent': Decimal('125000.00')
            },
            {
                'name': 'Mary Wanjiku',
                'email': 'mary@email.com',
                'phone': '0733-987654',
                'total_orders': 3,
                'total_spent': Decimal('78000.00')
            },
            {
                'name': 'Peter Ochieng',
                'email': 'peter@email.com',
                'phone': '0711-456789',
                'total_orders': 8,
                'total_spent': Decimal('210000.00')
            },
            {
                'name': 'Grace Akinyi',
                'email': 'grace@email.com',
                'phone': '0744-321654',
                'total_orders': 2,
                'total_spent': Decimal('45000.00')
            }
        ]
        
        for cust_data in customers_data:
            customer, created = POSCustomer.objects.get_or_create(
                email=cust_data['email'],
                defaults=cust_data
            )
            if created:
                self.stdout.write(f'Created customer: {customer.name}')
            else:
                self.stdout.write(f'Customer already exists: {customer.name}')
        
        # Create sample POS Sales
        if POSSale.objects.count() == 0:
            john = POSCustomer.objects.get(email='john@email.com')
            mary = POSCustomer.objects.get(email='mary@email.com')
            
            # Sample sale 1 - Restaurant
            sale1 = POSSale.objects.create(
                order_id='ORD-001',
                customer=john,
                payment_method='cash',
                subtotal=Decimal('1200.00'),
                discount=Decimal('0.00'),
                tax=Decimal('192.00'),
                total=Decimal('1392.00')
            )
            
            steak = POSProduct.objects.get(sku='RES-002')
            POSSaleItem.objects.create(
                sale=sale1,
                product=steak,
                quantity=1,
                price=Decimal('1200.00'),
                total=Decimal('1200.00')
            )
            
            # Sample sale 2 - Coffee Shop
            sale2 = POSSale.objects.create(
                order_id='ORD-002',
                customer=mary,
                payment_method='mpesa',
                subtotal=Decimal('730.00'),
                discount=Decimal('0.00'),
                tax=Decimal('116.80'),
                total=Decimal('846.80')
            )
            
            cappuccino = POSProduct.objects.get(sku='COF-002')
            muffin = POSProduct.objects.get(sku='COF-005')
            POSSaleItem.objects.create(
                sale=sale2,
                product=cappuccino,
                quantity=1,
                price=Decimal('350.00'),
                total=Decimal('350.00')
            )
            POSSaleItem.objects.create(
                sale=sale2,
                product=muffin,
                quantity=1,
                price=Decimal('180.00'),
                total=Decimal('180.00')
            )
            
            self.stdout.write('Created sample POS sales')
        else:
            self.stdout.write('POS sales already exist')
        
        self.stdout.write(self.style.SUCCESS('POS demo data populated successfully!'))