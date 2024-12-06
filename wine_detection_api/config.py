import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MODEL_PATH = os.getenv('MODEL_PATH', 'app/models/best.pt')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', False)
