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
from typing import List, Dict, Optional
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
    
    # Use this to fetch PR metadata before deeper operations like file scanning or status updates
    def get_pr_details(self, repo_name: str, pr_number: int) -> Dict:
        """
        Get detailed information about a Pull Request
        
        Args:
            repo_name: Full repo name
            pr_number: Pull request number
            
        Returns:
            Dictionary with PR details
        """
        try:
            repo = self.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            details = {
                'number': pr.number,
                'title': pr.title,
                'body': pr.body or '',
                'author': pr.user.login,
                'author_avatar': pr.user.avatar_url,
                'base_branch': pr.base.ref,
                'head_branch': pr.head.ref,
                'sha': pr.head.sha,
                'url': pr.html_url,
                'state': pr.state,
                'mergeable': pr.mergeable,
                'created_at': pr.created_at.isoformat(),
                'updated_at': pr.updated_at.isoformat()
            }
            logger.info(f"✅ Retrieved details for PR #{pr_number}")
            return details
        except GithubException as e:
            logger.error(f"❌ Failed to get PR details: {e}")
            raise
    
    # Critical for scanning code changes; uses PR details for context
    def get_pr_files(self, repo_name: str, pr_number: int) -> List[Dict]:
        """
        Get list of files changed in a Pull Request with their diffs
        
        This is the CRITICAL function that gets the actual code changes to scan!
        
        Args:
            repo_name: Full repo name (e.g., 'myorg/myrepo')
            pr_number: Pull request number
            
        Returns:
            List of dictionaries containing file information:
            [
                {
                    'filename': 'path/to/file.py',
                    'status': 'added' | 'modified' | 'removed' | 'renamed',
                    'additions': 10,
                    'deletions': 5,
                    'changes': 15,
                    'patch': '@@ -1,3 +1,4 @@ ...',  # The actual diff!
                    'blob_url': 'https://github.com/...',
                    'raw_url': 'https://raw.githubusercontent.com/...'
                },
                ...
            ]
            
        Raises:
            GithubException: If PR doesn't exist or no access
        """
        try:
            repo = self.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            logger.info(f"📁 Fetching files for PR #{pr_number}: {pr.title}")
            
            files_changed = []
            total_files = 0
            skipped_files = 0
            
            for file in pr.get_files():
                total_files += 1
                
                # Only process text files (skip binaries, images, etc.)
                if self._is_text_file(file.filename):
                    file_info = {
                        'filename': file.filename,
                        'status': file.status,
                        'additions': file.additions,
                        'deletions': file.deletions,
                        'changes': file.changes,
                        'patch': file.patch,  # This is the diff!
                        'blob_url': file.blob_url,
                        'raw_url': file.raw_url
                    }
                    files_changed.append(file_info)
                    logger.debug(f"   ✅ {file.filename} ({file.status})")
                else:
                    skipped_files += 1
                    logger.debug(f"   ⏭️  Skipping binary: {file.filename}")
            
            logger.info(f"✅ Found {len(files_changed)} text files to scan "
                       f"({skipped_files} binaries skipped out of {total_files} total)")
            
            return files_changed
            
        except GithubException as e:
            logger.error(f"❌ Failed to fetch PR files: {e}")
            raise
    
    # For providing feedback after scans
    def post_comment(self, repo_name: str, pr_number: int, comment: str) -> bool:
        """
        Post a comment on a Pull Request
        
        Args:
            repo_name: Full repo name (e.g., 'myorg/myrepo')
            pr_number: Pull request number
            comment: Comment text (supports markdown)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = self.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            logger.info(f"✅ Posted comment to PR #{pr_number} in {repo_name}")
            return True
        except GithubException as e:
            logger.error(f"❌ Failed to post comment: {e}")
            return False
    
    # For gating merges based on scan results; requires SHA from get_pr_details
    def set_commit_status(
        self,
        repo_name: str,
        sha: str,
        state: str,
        description: str,
        context: str = "ATF Sentinel Security Scan",
        target_url: Optional[str] = None
    ) -> bool:
        """
        Set commit status (controls PR merge button)
        This is THE critical function that blocks PRs!
        
        Args:
            repo_name: Full repo name
            sha: Commit SHA (from PR head)
            state: 'success' | 'failure' | 'pending' | 'error'
            description: Status description (max 140 chars)
            context: Status check name (appears in PR)
            target_url: Optional URL to link to (e.g., dashboard)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = self.get_repo(repo_name)
            commit = repo.get_commit(sha)
            # Truncate description if too long (GitHub limit is 140 chars)
            description = description[:140] if len(description) > 140 else description
            # Set the status
            commit.create_status(
                state=state,
                description=description,
                context=context,
                target_url=target_url
            )
            emoji = {
                'success': '✅',
                'failure': '❌',
                'pending': '⏳',
                'error': '⚠️'
            }.get(state, '📌')
            logger.info(f"{emoji} Set commit status: {state} - {description}")
            return True
        except GithubException as e:
            logger.error(f"❌ Failed to set commit status: {e}")
            return False
    
    @staticmethod
    def _is_text_file(filename: str) -> bool:
        """
        Check if file is a text file (should be scanned) vs binary (skip)
        
        Args:
            filename: Name of the file with extension
            
        Returns:
            True if text file that should be scanned, False otherwise
        """
        # Programming languages
        text_extensions = {
            # Python
            '.py', '.pyw', '.pyx', '.pxd', '.pxi',
            
            # JavaScript/TypeScript
            '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
            
            # Java/Kotlin/Scala
            '.java', '.kt', '.kts', '.scala',
            
            # C/C++
            '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx',
            
            # C#/.NET
            '.cs', '.vb', '.fs',
            
            # Go
            '.go',
            
            # Rust
            '.rs',
            
            # Ruby
            '.rb', '.rake', '.gemspec',
            
            # PHP
            '.php', '.phtml', '.php3', '.php4', '.php5', '.phps',
            
            # Swift
            '.swift',
            
            # Objective-C
            '.m', '.mm',
            
            # R
            '.r', '.R',
            
            # Web
            '.html', '.htm', '.xhtml', '.css', '.scss', '.sass', '.less',
            '.vue', '.svelte', '.astro',
            
            # Config/Data
            '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.conf', '.config',
            '.env', '.properties', '.cfg',
            
            # Scripts
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            
            # Documentation
            '.md', '.markdown', '.txt', '.rst', '.asciidoc', '.adoc',
            
            # SQL
            '.sql', '.pgsql', '.mysql', '.plsql',
            
            # GraphQL
            '.graphql', '.gql',
            
            # Terraform
            '.tf', '.tfvars',
            
            # Docker
            '.dockerfile',
        }
        
        filename_lower = filename.lower()
        
        # Check extension
        for ext in text_extensions:
            if filename_lower.endswith(ext):
                return True
        
        # Check exact matches (files without extensions)
        basename = filename.split('/')[-1].lower()
        text_basenames = {
            'dockerfile', 'makefile', 'rakefile', 'gemfile',
            'readme', 'license', 'changelog', 'contributing',
            'jenkinsfile', 'vagrantfile', 'procfile'
        }
        
        if basename in text_basenames:
            return True
        
        # Skip known binary/media extensions
        binary_extensions = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp',
            # Videos
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
            # Audio
            '.mp3', '.wav', '.flac', '.aac', '.ogg',
            # Archives
            '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
            # Executables
            '.exe', '.dll', '.so', '.dylib', '.bin',
            # Documents
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Fonts
            '.ttf', '.otf', '.woff', '.woff2', '.eot',
            # Other
            '.pyc', '.pyo', '.class', '.o', '.a', '.jar', '.war'
        }
        
        for ext in binary_extensions:
            if filename_lower.endswith(ext):
                return False
        
        # Default to True for unknown extensions (safer to scan)
        return True


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


# Test function for PR file fetching
def test_pr_file_fetching():
    """
    Test PR file fetching functionality
    """
    import os
    
    print("\n🧪 Testing PR File Fetching\n")
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
        # Initialize client
        print("\n1️⃣  Initializing GitHub client...")
        client = GitHubClient(token)
        print("   ✅ Client initialized\n")
        
        # Get PR details from user
        print("2️⃣  Enter Pull Request details to test:")
        print("   " + "-"*56)
        repo_name = input("   Repository (owner/repo): ").strip()
        
        if not repo_name:
            print("\n   Using default: octocat/Hello-World")
            repo_name = "octocat/Hello-World"
        
        pr_number = input("   PR number: ").strip()
        
        if not pr_number:
            print("   ❌ PR number is required")
            return False
        
        pr_number = int(pr_number)
        print()
        
        # Fetch PR files
        print(f"3️⃣  Fetching files from PR #{pr_number}...")
        print("   " + "-"*56)
        files = client.get_pr_files(repo_name, pr_number)
        
        if not files:
            print("   ⚠️  No text files found in this PR")
            print("   (PR may contain only binary files or be empty)\n")
            return True
        
        print(f"   ✅ Found {len(files)} text files\n")
        
        # Display file details
        print("4️⃣  File Details:")
        print("   " + "-"*56)
        
        for i, file in enumerate(files, 1):
            status_emoji = {
                'added': '🆕',
                'modified': '📝',
                'removed': '🗑️',
                'renamed': '🔄'
            }.get(file['status'], '📄')
            
            print(f"\n   {status_emoji} File #{i}: {file['filename']}")
            print(f"      Status:    {file['status']}")
            print(f"      Changes:   +{file['additions']} -{file['deletions']} (~{file['changes']} lines)")
            print(f"      Blob URL:  {file['blob_url']}")
            
            # Show diff preview
            if file['patch']:
                patch_lines = file['patch'].split('\n')
                print(f"      Diff preview ({len(patch_lines)} lines):")
                # Show first 5 lines of diff
                for line in patch_lines[:5]:
                    preview = line[:70] + '...' if len(line) > 70 else line
                    print(f"         {preview}")
                if len(patch_lines) > 5:
                    print(f"         ... ({len(patch_lines) - 5} more lines)")
            else:
                print(f"      Diff:      (No patch available)")
        
        print()
        
        # Statistics
        print("5️⃣  Statistics:")
        print("   " + "-"*56)
        
        total_additions = sum(f['additions'] for f in files)
        total_deletions = sum(f['deletions'] for f in files)
        total_changes = sum(f['changes'] for f in files)
        
        status_counts = {}
        for file in files:
            status = file['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"   Total files:     {len(files)}")
        print(f"   Total additions: +{total_additions}")
        print(f"   Total deletions: -{total_deletions}")
        print(f"   Total changes:   ~{total_changes} lines")
        print(f"\n   By status:")
        for status, count in sorted(status_counts.items()):
            emoji = {
                'added': '🆕',
                'modified': '📝',
                'removed': '🗑️',
                'renamed': '🔄'
            }.get(status, '📄')
            print(f"      {emoji} {status.capitalize()}: {count}")
        
        print()
        
        # Test data structure
        print("6️⃣  Verifying data structure...")
        print("   " + "-"*56)
        
        required_keys = ['filename', 'status', 'additions', 'deletions', 
                        'changes', 'patch', 'blob_url', 'raw_url']
        
        for file in files:
            for key in required_keys:
                assert key in file, f"Missing key: {key}"
        
        print(f"   ✅ All {len(required_keys)} required fields present")
        print(f"   ✅ Data structure validation passed\n")
        
        # Summary
        print("="*60)
        print("✅ PR File Fetching Test Passed!\n")
        print("📊 Summary:")
        print(f"   • Repository:  {repo_name}")
        print(f"   • PR Number:   #{pr_number}")
        print(f"   • Files found: {len(files)}")
        print(f"   • Changes:     +{total_additions} -{total_deletions}")
        print()
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}\n")
        return False
    except GithubException as e:
        print(f"\n❌ GitHub error: {e}\n")
        print("   Possible reasons:")
        print("   • PR doesn't exist")
        print("   • Repository is private and token lacks access")
        print("   • Invalid repository name format")
        print()
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pr_file_fetching()
    exit(0 if success else 1)