"""
GitHub API Client for ATF Sentinel
Handles all interactions with GitHub API including:
- Fetching PR files and diffs
- Posting comments
- Setting commit status
Author: ANIRUDH S J
"""
from github import Github
from github.GithubException import GithubException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubClient:
    """
    Wrapper around PyGithub for ATF Sentinel operations
    Provides simplified interface for common GitHub actions
    """
    
    def __init__(self, token: str):
        """
        Initialize GitHub client with authentication
        
        Args:
            token: GitHub Personal Access Token with repo permissions
            
        Raises:
            ValueError: If token is empty or None
            GithubException: If authentication fails
        """
        if not token:
            raise ValueError("GitHub token is required")
        
        self.gh = Github(token)
        self.token = token
        
        # Verify token is valid by getting authenticated user
        try:
            user = self.gh.get_user()
            logger.info(f"✅ GitHub client initialized for user: {user.login}")
            logger.info(f"   Rate limit: {self.gh.get_rate_limit().core.remaining}/5000")
        except GithubException as e:
            logger.error(f"❌ Failed to authenticate with GitHub: {e}")
            raise
    
    def get_repo(self, repo_name: str):
        """
        Get repository object
        
        Args:
            repo_name: Full repo name (e.g., 'octocat/Hello-World')
            
        Returns:
            Repository object from PyGithub
            
        Raises:
            GithubException: If repo doesn't exist or no access
        """
        try:
            repo = self.gh.get_repo(repo_name)
            logger.info(f"✅ Accessed repository: {repo_name}")
            return repo
        except GithubException as e:
            logger.error(f"❌ Failed to access repo {repo_name}: {e}")
            raise


if __name__ == "__main__":
    print("✅ GitHub client module loaded successfully")
    print("Use test_commit2_1.py to test repository access")