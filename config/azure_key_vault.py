from dotenv import load_dotenv
import os 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

load_dotenv()

VAULT_URL = os.getenv("VAULT_URL")
assert VAULT_URL, 'VAULT_URL is not set in .env'

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)
