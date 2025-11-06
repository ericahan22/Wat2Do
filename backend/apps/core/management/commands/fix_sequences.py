from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequences that are out of sync for all tables'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get all sequences and their associated tables using pg_catalog
            cursor.execute("""
                SELECT 
                    s.relname AS sequence_name,
                    t.relname AS table_name,
                    a.attname AS column_name
                FROM pg_class s
                JOIN pg_depend d ON d.objid = s.oid
                JOIN pg_class t ON t.oid = d.refobjid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
                JOIN pg_namespace n ON n.oid = s.relnamespace
                WHERE s.relkind = 'S'
                  AND n.nspname = 'public'
                ORDER BY t.relname, a.attname;
            """)
            
            sequences = cursor.fetchall()
            fixed_count = 0
            
            if not sequences:
                self.stdout.write(self.style.WARNING("No sequences found in the public schema"))
                return
            
            self.stdout.write(f"Found {len(sequences)} sequences to check...")
            self.stdout.write("")
            
            for sequence_name, table_name, column_name in sequences:
                try:
                    # Get the current max value in the table
                    cursor.execute(f"SELECT MAX({column_name}) FROM {table_name};")
                    max_value = cursor.fetchone()[0]
                    
                    if max_value is None:
                        max_value = 1
                    
                    # Get the current sequence value
                    cursor.execute(f"SELECT last_value FROM {sequence_name};")
                    current_seq_value = cursor.fetchone()[0]
                    
                    # Fix the sequence if needed
                    if current_seq_value < max_value:
                        cursor.execute(f"SELECT setval('{sequence_name}', {max_value}, true);")
                        new_value = cursor.fetchone()[0]
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Fixed {table_name}.{column_name}: {sequence_name} "
                                f"({current_seq_value} → {new_value})"
                            )
                        )
                        fixed_count += 1
                    else:
                        self.stdout.write(
                            f"  {table_name}.{column_name}: {sequence_name} is OK (current: {current_seq_value}, max: {max_value})"
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Error fixing {table_name}.{column_name}: {str(e)}")
                    )
            
            self.stdout.write("")
            self.stdout.write("="*60)
            if fixed_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully fixed {fixed_count} sequence(s)!"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("✓ All sequences are already in sync!")
                )

