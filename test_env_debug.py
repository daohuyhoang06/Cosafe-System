from dotenv import load_dotenv
import os

load_dotenv()

print("ES_CLOUD_URL:", os.getenv("ES_CLOUD_URL"))
print("ES_API_KEY:", os.getenv("ES_API_KEY"))
