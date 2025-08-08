from supabase import create_client
from datetime import datetime
import uuid
from django.conf import settings

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
