import os
from cryptography.fernet import Fernet

# Database
DATABASE_URL = "sqlite:///./civicshield.db"

# Mode
EDGE_MODE = True

# Bandwidth tracking (bytes)
TOTAL_BANDWIDTH_USED = 0

# Encryption key (persistent for runtime)
# In production this would be securely stored
ENCRYPTION_KEY = Fernet.generate_key()
FERNET = Fernet(ENCRYPTION_KEY)

# Secure raw storage path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECURE_RAW_FOLDER = os.path.join(BASE_DIR, "secure_raw")

# Ensure folder exists
os.makedirs(SECURE_RAW_FOLDER, exist_ok=True)