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


# Test function for file type detection
def test_file_type_detection():
    """
    Test the _is_text_file method with various file types
    """
    print("\n🧪 Testing File Type Detection\n")
    print("="*60)
    
    # Test cases: (filename, expected_result, category)
    test_cases = [
        # Programming languages
        ('main.py', True, 'Python'),
        ('app.js', True, 'JavaScript'),
        ('component.tsx', True, 'TypeScript React'),
        ('Main.java', True, 'Java'),
        ('lib.rs', True, 'Rust'),
        ('app.go', True, 'Go'),
        ('script.rb', True, 'Ruby'),
        ('index.php', True, 'PHP'),
        ('program.c', True, 'C'),
        ('program.cpp', True, 'C++'),
        ('App.cs', True, 'C#'),
        ('app.swift', True, 'Swift'),
        
        # Web files
        ('index.html', True, 'HTML'),
        ('styles.css', True, 'CSS'),
        ('styles.scss', True, 'SCSS'),
        ('App.vue', True, 'Vue'),
        ('Component.svelte', True, 'Svelte'),
        
        # Config files
        ('config.json', True, 'JSON'),
        ('config.yaml', True, 'YAML'),
        ('config.yml', True, 'YAML'),
        ('config.toml', True, 'TOML'),
        ('.env', True, 'Environment'),
        ('settings.ini', True, 'INI'),
        
        # Scripts
        ('build.sh', True, 'Shell'),
        ('deploy.bash', True, 'Bash'),
        ('script.ps1', True, 'PowerShell'),
        
        # Documentation
        ('README.md', True, 'Markdown'),
        ('CHANGELOG.txt', True, 'Text'),
        ('docs.rst', True, 'reStructuredText'),
        
        # Files without extensions
        ('Dockerfile', True, 'Docker'),
        ('Makefile', True, 'Make'),
        ('Jenkinsfile', True, 'Jenkins'),
        ('Gemfile', True, 'Ruby Gem'),
        
        # SQL
        ('schema.sql', True, 'SQL'),
        ('query.pgsql', True, 'PostgreSQL'),
        
        # GraphQL & Terraform
        ('schema.graphql', True, 'GraphQL'),
        ('main.tf', True, 'Terraform'),
        
        # Binary files (should be False)
        ('image.png', False, 'PNG Image'),
        ('photo.jpg', False, 'JPEG Image'),
        ('icon.svg', False, 'SVG Image'),
        ('video.mp4', False, 'MP4 Video'),
        ('audio.mp3', False, 'MP3 Audio'),
        ('archive.zip', False, 'ZIP Archive'),
        ('archive.tar.gz', False, 'TAR.GZ Archive'),
        ('program.exe', False, 'Executable'),
        ('library.dll', False, 'DLL'),
        ('library.so', False, 'Shared Object'),
        ('document.pdf', False, 'PDF'),
        ('spreadsheet.xlsx', False, 'Excel'),
        ('font.ttf', False, 'TrueType Font'),
        ('compiled.pyc', False, 'Python Compiled'),
        ('compiled.class', False, 'Java Compiled'),
        
        # Edge cases
        ('file.UNKNOWN', True, 'Unknown (defaults to True)'),
        ('path/to/file.py', True, 'Nested path'),
        ('README', True, 'No extension'),
    ]
    
    print("\n1️⃣  Testing Text Files (Should be scanned)\n")
    text_passed = 0
    text_total = sum(1 for _, expected, _ in test_cases if expected)
    
    for filename, expected, category in test_cases:
        if expected:  # Only test text files in this section
            result = GitHubClient._is_text_file(filename)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {filename:<30} [{category}]")
            if result == expected:
                text_passed += 1
    
    print(f"\n   Result: {text_passed}/{text_total} text files detected correctly\n")
    
    print("\n2️⃣  Testing Binary Files (Should be skipped)\n")
    binary_passed = 0
    binary_total = sum(1 for _, expected, _ in test_cases if not expected)
    
    for filename, expected, category in test_cases:
        if not expected:  # Only test binary files in this section
            result = GitHubClient._is_text_file(filename)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {filename:<30} [{category}]")
            if result == expected:
                binary_passed += 1
    
    print(f"\n   Result: {binary_passed}/{binary_total} binary files detected correctly\n")
    
    # Summary
    total_passed = text_passed + binary_passed
    total_cases = text_total + binary_total
    
    print("="*60)
    print(f"📊 Test Summary:\n")
    print(f"   Text files:   {text_passed}/{text_total} ✅")
    print(f"   Binary files: {binary_passed}/{binary_total} ✅")
    print(f"   Total:        {total_passed}/{total_cases} ✅")
    
    if total_passed == total_cases:
        print(f"\n✅ All file type detection tests passed!\n")
        return True
    else:
        print(f"\n❌ {total_cases - total_passed} tests failed!\n")
        return False


if __name__ == "__main__":
    success = test_file_type_detection()
    exit(0 if success else 1)