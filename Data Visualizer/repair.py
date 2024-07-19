import os
import threading
from supabase import create_client, Client

# Read the environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
# Create a new Supabase client
supabase: Client = create_client(url, key)

def worker(data, supabase):
    for eachLine in data:
        try:
            id = eachLine.split(',')[0]
            province = eachLine.split(',')[6]
            print(id, province)
            supabase.table('covid').update({'province_of_isolation': province}).eq('id', id).execute()
        except:
            pass

with open('../confirmed-cases (version 1).csv', 'r', encoding='UTF-8') as file:
    group_amount = 50
    data = file.read().split('\n')
    data_group = [data[i:i+(676870//group_amount)] for i in range(8141, len(data), 676870//group_amount)]
    for group in data_group:
        threading.Thread(target=worker, args=(group, supabase)).start()