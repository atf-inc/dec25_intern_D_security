# app/config.py
"""
Configuration management with GCP Secret Manager
Loads secrets and configuration for ATF Sentinel
Author: ANIRUDH S J
Date: DECEMBER 14, 2025
"""

import os
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
                logger.warning("⚠️  Could not determine GCP project ID")
                self.project_id = "unknown"
        
        logger.info(f"📦 Initializing config for project: {self.project_id}")
        
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info("✅ Secret Manager client initialized")
        except Exception as e:
            logger.error(f"❌ Could not initialize Secret Manager: {e}")
            raise
    
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
        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode('UTF-8')
            logger.info(f"✅ Loaded secret: {secret_name}")
            return secret_value
        except Exception as e:
            logger.error(f"❌ Could not load secret {secret_name} from GCP: {e}")
            raise


# Global config instance
config = Config()


# For testing this module directly
if __name__ == "__main__":
    print("\n🧪 Testing Configuration...\n")
    print("="*50)
    
    # Test project ID
    print(f"Project ID: {config.project_id}")
    
    # Test loading a secret
    try:
        token = config.get_secret('github-token')
        print(f"✅ Successfully loaded github-token ({len(token)} chars)")
    except Exception as e:
        print(f"❌ Failed to load secret: {e}")
    
    print("="*50)