import os
import environ

# Initialize environ
env = environ.Env()

# Path to the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, 'config', '.env')

# Read the .env file
if os.path.exists(ENV_FILE):
    env.read_env(ENV_FILE)
else:
    raise FileNotFoundError(f"Environment file not found at {ENV_FILE}")

# Example environment variables
GSHEET_KEY = env("GSHEET_KEY")
PRICING_WORKSHEET_KEY = env("PRICING_WORKSHEET_KEY")
DB_STRING = env("DB_STRING")
SQL_YAML_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'queries.yaml')
SUPABASE_URL = env("SUPABASE_URL")
SUPABASE_KEY = env("SUPABASE_KEY")
DEV_MODE= env("DEV_MODE")

## path
PRICING_PATH = {"prc_folder": env("PRICING_FOLDER"),
                "data_folder":'data/'}

SAMPLE_IMAGE_URL = ''
FX_RATES = 7.0
FX_SYMBOL = 'CHN'
