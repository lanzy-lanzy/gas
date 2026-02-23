from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.contrib.auth.models import User
from core.models import Order, LPGProduct, DeliveryLog, CustomerProfile
import time


class Command(BaseCommand):
    help = 'Test and optimize database performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-queries',
            action='store_true',
            help='Test common queries for performance',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all cached data',
        )
        parser.add_argument(
            '--analyze-db',
            action='store_true',
            help='Analyze database performance',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            self.clear_cache()
        
        if options['test_queries']:
            self.test_queries()
        
        if options['analyze_db']:
            self.analyze_database()

    def clear_cache(self):
        """Clear all cached data"""
        self.stdout.write('Clearing cache...')
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cache cleared successfully'))

    def test_queries(self):
        """Test common queries for performance"""
        self.stdout.write('Testing query performance...')
        
        queries_to_test = [
            {
                'name': 'Customer Dashboard Orders',
                'query': lambda: list(Order.objects.filter(customer_id=1).select_related('product')[:5])
            },
            {
                'name': 'Dealer Dashboard Stats',
                'query': lambda: {
                    'total_orders': Order.objects.count(),
                    'pending_orders': Order.objects.filter(status='pending').count(),
                    'low_stock': LPGProduct.objects.filter(current_stock__lte=10).count()
                }
            },
            {
                'name': 'Order Management List',
                'query': lambda: list(Order.objects.select_related('customer', 'product').all()[:25])
            },
            {
                'name': 'Inventory Dashboard',
                'query': lambda: list(LPGProduct.objects.filter(is_active=True).all())
            },
            {
                'name': 'Recent Deliveries',
                'query': lambda: list(DeliveryLog.objects.select_related('product', 'logged_by')[:10])
            }
        ]
        
        for test in queries_to_test:
            start_time = time.time()
            queries_before = len(connection.queries)
            
            try:
                result = test['query']()
                
                end_time = time.time()
                queries_after = len(connection.queries)
                
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                query_count = queries_after - queries_before
                
                status = self.style.SUCCESS('GOOD') if duration < 100 else self.style.WARNING('SLOW')
                if duration > 500:
                    status = self.style.ERROR('VERY SLOW')
                
                self.stdout.write(
                    f'{test["name"]}: {duration:.2f}ms, {query_count} queries - {status}'
                )
                
                if duration > 100:
                    self.stdout.write(
                        self.style.WARNING(f'  Consider optimizing this query')
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'{test["name"]}: ERROR - {str(e)}')
                )

    def analyze_database(self):
        """Analyze database structure and suggest optimizations"""
        self.stdout.write('Analyzing database structure...')
        
        # Check table sizes
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, 
                       (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=m.name) as index_count
                FROM sqlite_master m 
                WHERE type='table' AND name LIKE 'core_%'
            """)
            
            tables = cursor.fetchall()
            
            self.stdout.write('\nTable Analysis:')
            for table_name, index_count in tables:
                # Get row count
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                row_count = cursor.fetchone()[0]
                
                self.stdout.write(f'  {table_name}: {row_count} rows, {index_count} indexes')
                
                # Suggest optimizations based on row count
                if row_count > 1000 and index_count < 3:
                    self.stdout.write(
                        self.style.WARNING(f'    Consider adding more indexes to {table_name}')
                    )
        
        # Check for missing indexes on foreign keys
        self.stdout.write('\nForeign Key Index Analysis:')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.name as table_name, p.name as column_name
                FROM sqlite_master m
                JOIN pragma_foreign_key_list(m.name) p
                WHERE m.type = 'table' AND m.name LIKE 'core_%'
            """)
            
            foreign_keys = cursor.fetchall()
            for table, column in foreign_keys:
                # Check if index exists
                cursor.execute(f"""
                    SELECT COUNT(*) FROM pragma_index_list('{table}') 
                    WHERE name LIKE '%{column}%'
                """)
                
                index_exists = cursor.fetchone()[0] > 0
                if not index_exists:
                    self.stdout.write(
                        self.style.WARNING(f'  Missing index on {table}.{column}')
                    )
        
        # Performance recommendations
        self.stdout.write('\nPerformance Recommendations:')
        self.stdout.write('1. Use select_related() for foreign key relationships')
        self.stdout.write('2. Use prefetch_related() for reverse foreign keys')
        self.stdout.write('3. Add pagination for large datasets')
        self.stdout.write('4. Use database indexes on frequently queried fields')
        self.stdout.write('5. Cache expensive queries using Django cache framework')
        self.stdout.write('6. Use aggregate queries instead of Python loops')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase analysis complete'))