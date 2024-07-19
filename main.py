import os
from supabase import create_client, Client
from matplotlib.figure import Figure
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter.ttk import Combobox

# Read the environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
# Create a new Supabase client
supabase: Client = create_client(url, key)