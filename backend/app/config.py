"""
Configuration management with GCP Secret Manager
Loads secrets and configuration for ATF Sentinel
Author: ANIRUDH S J
"""
import os
import json
from google.cloud import secretmanager
from functools import lru_cache
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class that loads secrets from GCP Secret Manager
    """
   
    def __init__(self):
        """Initializing the Secret Manager client"""
        self.project_id = os.getenv('GCP_PROJECT_ID')
       
        if not self.project_id:
            # Try to get from gcloud config
            import subprocess
            try:
                result = subprocess.run(
                    ['gcloud', 'config', 'get-value', 'project'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.project_id = result.stdout.strip()
            except:
                logger.warning("⚠️ Could not determine GCP project ID")
                self.project_id = "unknown"
       
        logger.info(f"📦 Initializing config for project: {self.project_id}")
       
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info("✅ Secret Manager client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize Secret Manager (using env vars for local dev): {e}")
            self.client = None  # Allow local development without GCP credentials

        # Load core secrets with fallbacks to env vars for local dev
        self.github_token = os.getenv('GITHUB_TOKEN') or self._get_secret_safe('github-token')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET') or self._get_secret_safe('webhook-secret')
        allowed_repos_env = os.getenv('ALLOWED_REPOS', '').strip()
        if allowed_repos_env:
            try:
                self.allowed_repos = json.loads(allowed_repos_env)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Invalid JSON in ALLOWED_REPOS, using default")
                self.allowed_repos = ["testorg/*"]
        else:
            self.allowed_repos = self._get_secret_list_safe('allowed-repos') or ["testorg/*"]
        
        # Database configuration
        self.cloud_sql_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME', '')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_pass = os.getenv('DB_PASS') or self._get_secret_safe('db-password')
        self.db_name = os.getenv('DB_NAME', 'atf_sentinel')
        self.database_url = os.getenv(
            'DATABASE_URL',
            f'postgresql://{self.db_user}:{self.db_pass}@localhost:5432/{self.db_name}'
        )
        
        # Gemini AI configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') or self._get_secret_safe('gemini-api-key')
        
        # Slack configuration
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL') or self._get_secret_safe('slack-webhook-url')
        
        # Frontend URL for CORS
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
   
    def _get_secret_safe(self, secret_name: str) -> str:
        """Safely get secret with fallback to empty string."""
        try:
            return self.get_secret(secret_name)
        except Exception:
            logger.warning(f"⚠️ Falling back to empty {secret_name} (set env var for local)")
            return ""

    def _get_secret_list_safe(self, secret_name: str) -> list:
        """Safely get secret as list with fallback."""
        try:
            secret_val = self.get_secret(secret_name)
            return json.loads(secret_val)
        except Exception:
            return ["testorg/*"]  # Default fallback
   
    @lru_cache(maxsize=32)
    def get_secret(self, secret_name: str) -> str:
        """
        Fetch secret from GCP Secret Manager
       
        Args:
            secret_name: Name of the secret (e.g., 'github-token')
           
        Returns:
            Secret value as string
           
        Raises:
            Exception if secret cannot be loaded
        """
        if self.client is None:
            raise Exception("Secret Manager client not initialized (use env vars for local dev)")
        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode('UTF-8')
            logger.info(f"✅ Loaded secret: {secret_name}")
            return secret_value
        except Exception as e:
            logger.error(f"❌ Could not load secret {secret_name} from GCP: {e}")
            raise

    def validate(self) -> bool:
        """
        Validate critical configuration values.
        Returns True if all required fields are set, False otherwise.
        """
        required_fields = [
            self.github_token,
            self.webhook_secret,
        ]
        is_valid = all(field and str(field).strip() for field in required_fields)
        if self.allowed_repos:
            is_valid = is_valid and len(self.allowed_repos) > 0
        if not is_valid:
            logger.warning("⚠️ Configuration validation failed: Missing required secrets.")
        else:
            logger.info("✅ All configuration validated")
        return is_valid
    
    def get_database_config(self) -> dict:
        """Get database configuration as dictionary."""
        return {
            "cloud_sql_connection_name": self.cloud_sql_connection_name,
            "db_user": self.db_user,
            "db_name": self.db_name,
            "database_url": self.database_url,
            "has_password": bool(self.db_pass),
        }
   
# Global config instance
config = Config()

# For testing this module directly
if __name__ == "__main__":
    print("\n🧪 Testing Configuration...\n")
    print("="*50)
   
    # Test project ID
    print(f"Project ID: {config.project_id}")
   
    # Test validation
    print(f"Validation: {config.validate()}")
   
    # Test loading a secret
    try:
        token = config.github_token
        print(f"✅ GitHub Token loaded ({len(token)} chars)")
    except Exception as e:
        print(f"❌ Failed to load GitHub token: {e}")
   
    print("="*50)