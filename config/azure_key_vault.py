from dotenv import load_dotenv
import os 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def load_keyvault() -> SecretClient:
    load_dotenv()
    vault_url = os.getenv("VAULT_URL")
    if vault_url is None:
        raise EnvironmentError('VAULT_URL is not set in .env file')

    credential = DefaultAzureCredential()

    return SecretClient(vault_url=vault_url, credential=credential)
