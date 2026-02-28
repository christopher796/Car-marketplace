import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry

# Create each table separately with individual transactions
models_to_create = [User, Group, Permission, ContentType, Session, LogEntry]

for model in models_to_create:
    try:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)
        print(f'✓ Created table: {model._meta.db_table}')
    except Exception as e:
        error_msg = str(e)
        if 'already exists' in error_msg:
            print(f'✓ Table {model._meta.db_table} already exists')
        else:
            print(f'✗ Error for {model._meta.db_table}: {error_msg[:100]}')
    finally:
        # Close connection after each table
        connection.close()

print("\nDone creating tables!")
