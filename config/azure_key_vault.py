from dotenv import load_dotenv
import os 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

load_dotenv()

VAULT_URL = os.getenv("VAULT_URL")
if VAULT_URL is None:
    raise EnvironmentError('VAULT_URL is not set in .env file')

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)
