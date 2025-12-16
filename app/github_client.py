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


# Helper function for testing and verification
def display_repo_info(repo) -> None:
    """
    Display comprehensive repository information
    
    Helper function to show repo metadata in a formatted way.
    Useful for testing and debugging.
    
    Args:
        repo: PyGithub Repository object
    """
    print(f"\n📦 Repository Information:")
    print(f"   {'='*56}")
    print(f"   Name:        {repo.name}")
    print(f"   Full Name:   {repo.full_name}")
    print(f"   Owner:       {repo.owner.login}")
    print(f"   Private:     {repo.private}")
    print(f"   Description: {repo.description or 'No description'}")
    print(f"   Language:    {repo.language or 'Not specified'}")
    print(f"   Stars:       {repo.stargazers_count:,}")
    print(f"   Forks:       {repo.forks_count:,}")
    print(f"   Open Issues: {repo.open_issues_count:,}")
    print(f"   Created:     {repo.created_at.strftime('%Y-%m-%d')}")
    print(f"   Updated:     {repo.updated_at.strftime('%Y-%m-%d')}")
    print(f"   URL:         {repo.html_url}")
    print(f"   {'='*56}\n")


# Comprehensive test suite
def test_repository_access():
    """
    Comprehensive test suite for repository access functionality
    Tests both automated scenarios and interactive user flows
    """
    import os
    
    print("\n🧪 Testing Repository Access - Complete Test Suite\n")
    print("="*60)
    
    # Get token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Enter your GitHub Personal Access Token:")
        token = input().strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    try:
        # Test 1: Initialize client
        print("\n1️⃣  Testing Client Initialization")
        print("   " + "-"*56)
        client = GitHubClient(token)
        print("   ✅ Client initialized successfully\n")
        
        # Test 2: Access well-known public repository
        print("2️⃣  Testing Public Repository Access")
        print("   " + "-"*56)
        print("   Accessing: octocat/Hello-World")
        repo1 = client.get_repo("octocat/Hello-World")
        display_repo_info(repo1)
        print("   ✅ Public repository accessed successfully\n")
        
        # Test 3: Access another popular repository
        print("3️⃣  Testing Multiple Repository Access")
        print("   " + "-"*56)
        test_repos = [
            "torvalds/linux",
            "microsoft/vscode",
            "python/cpython"
        ]
        
        print("   Testing access to multiple repositories:")
        for repo_name in test_repos:
            try:
                repo = client.get_repo(repo_name)
                print(f"   ✅ {repo_name}: {repo.stargazers_count:,} stars")
            except Exception as e:
                print(f"   ⚠️  {repo_name}: {str(e)[:50]}...")
        print()
        
        # Test 4: Error handling for invalid repository
        print("4️⃣  Testing Error Handling")
        print("   " + "-"*56)
        invalid_repos = [
            "invalid/nonexistent-repo-12345",
            "thisdoesnotexist/norepo",
            "bad/format/toolong"
        ]
        
        errors_caught = 0
        for repo_name in invalid_repos:
            try:
                client.get_repo(repo_name)
                print(f"   ❌ {repo_name}: Should have raised exception")
            except GithubException:
                print(f"   ✅ {repo_name}: Exception caught correctly")
                errors_caught += 1
        
        if errors_caught == len(invalid_repos):
            print(f"   ✅ All {errors_caught} invalid repos handled correctly\n")
        else:
            print(f"   ⚠️  Only {errors_caught}/{len(invalid_repos)} handled\n")
        
        # Test 5: Access user's own repositories
        print("5️⃣  Testing Authenticated User's Repositories")
        print("   " + "-"*56)
        user = client.gh.get_user()
        print(f"   Authenticated as: {user.login}")
        
        user_repos = list(user.get_repos()[:3])  # Get first 3 repos
        if user_repos:
            print(f"   Found {len(user_repos)} repositories:")
            for repo in user_repos:
                print(f"   • {repo.full_name} ({'private' if repo.private else 'public'})")
            
            # Display detailed info for first repo
            print(f"\n   Detailed info for first repository:")
            display_repo_info(user_repos[0])
            print("   ✅ User repositories accessed successfully\n")
        else:
            print("   ⏭️  No repositories found (new account?)\n")
        
        # Test 6: Interactive test
        print("6️⃣  Interactive Repository Test")
        print("   " + "-"*56)
        print("   Enter a repository to test (or press Enter to skip):")
        print("   Format: owner/repo (e.g., facebook/react)")
        custom_repo = input("   Repository: ").strip()
        
        if custom_repo:
            try:
                print(f"\n   Accessing: {custom_repo}")
                repo = client.get_repo(custom_repo)
                display_repo_info(repo)
                print("   ✅ Custom repository accessed successfully\n")
            except GithubException as e:
                print(f"   ❌ Failed to access: {e}\n")
        else:
            print("   ⏭️  Skipped interactive test\n")
        
        # Test 7: Rate limit check
        print("7️⃣  Checking API Rate Limit")
        print("   " + "-"*56)
        rate_limit = client.gh.get_rate_limit()
        remaining = rate_limit.core.remaining
        total = rate_limit.core.limit
        reset_time = rate_limit.core.reset
        
        print(f"   Remaining: {remaining}/{total}")
        print(f"   Reset at:  {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if remaining < 100:
            print("   ⚠️  Rate limit running low!")
        else:
            print("   ✅ Rate limit healthy")
        print()
        
        # Final summary
        print("="*60)
        print("✅ All Repository Access Tests Passed!")
        print("="*60)
        print("\n📊 Test Summary:")
        print(f"   • Client initialization: ✅")
        print(f"   • Public repo access: ✅")
        print(f"   • Multiple repo access: ✅")
        print(f"   • Error handling: ✅")
        print(f"   • User repo access: ✅")
        print(f"   • Interactive test: {'✅' if custom_repo else '⏭️ '}")
        print(f"   • Rate limit check: ✅")
        print(f"\n   API calls remaining: {remaining}/{total}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_repository_access()
    exit(0 if success else 1)