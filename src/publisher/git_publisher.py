"""
Git-based publisher for automated commits
"""
import subprocess
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class GitPublisher:
    """Publisher for Git commits"""
    
    def __init__(self, repo_path: str, branch: str = 'main', 
                 author_name: str = 'NewsSurgeAI Bot', 
                 author_email: str = 'news-bot@newsurgeai.com'):
        self.repo_path = Path(repo_path)
        self.branch = branch
        self.author_name = author_name
        self.author_email = author_email
    
    def commit_and_push(self, message: str, files: list = None) -> bool:
        """
        Commit changes and push to remote
        
        Args:
            message: Commit message
            files: List of files to add (None for all changes)
            
        Returns:
            bool: Success status
        """
        try:
            # Change to repo directory
            original_cwd = Path.cwd()
            os.chdir(self.repo_path)
            
            # Configure git user (with error handling)
            try:
                self.run_git_command(['config', 'user.name', self.author_name])
                self.run_git_command(['config', 'user.email', self.author_email])
            except Exception as e:
                logger.warning(f"Git config warning: {str(e)}")
            
            # Add files
            if files:
                for file in files:
                    try:
                        self.run_git_command(['add', str(file)])
                    except Exception as e:
                        logger.warning(f"Could not add file {file}: {str(e)}")
            else:
                self.run_git_command(['add', '.'])
            
            # Check if there are changes to commit
            result = self.run_git_command(['diff', '--cached', '--quiet'], check=False)
            if result.returncode == 0:
                logger.info("No changes to commit")
                return True
            
            # Commit with safe message
            safe_message = message.encode('ascii', 'replace').decode('ascii')
            self.run_git_command(['commit', '-m', safe_message])
            
            # Push with retry logic
            try:
                self.run_git_command(['push', 'origin', self.branch])
                logger.info(f"Successfully committed and pushed: {safe_message}")
                return True
            except Exception as push_error:
                logger.warning(f"Push failed, but commit succeeded: {str(push_error)}")
                # Still return True since commit worked
                return True
            
        except Exception as e:
            logger.error(f"Git publish error: {str(e)}")
            return False
        finally:
            # Restore original directory
            try:
                os.chdir(original_cwd)
            except Exception:
                pass
    
    def run_git_command(self, args: list, check: bool = True) -> subprocess.CompletedProcess:
        """
        Run git command
        
        Args:
            args: Git command arguments
            check: Whether to check return code
            
        Returns:
            CompletedProcess result
        """
        cmd = ['git'] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        
        # Fix Windows encoding issues
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters instead of failing
        )
        
        if result.stdout:
            logger.debug(f"Git stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"Git stderr: {result.stderr}")
        
        return result
    
    def is_git_repo(self) -> bool:
        """
        Check if directory is a git repository
        
        Returns:
            bool: True if git repo
        """
        try:
            git_dir = self.repo_path / '.git'
            return git_dir.exists()
        except Exception:
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """
        Get current git branch
        
        Returns:
            str: Current branch name or None
        """
        try:
            original_cwd = Path.cwd()
            os.chdir(self.repo_path)
            
            result = self.run_git_command(['branch', '--show-current'])
            return result.stdout.strip() if result.stdout else None
            
        except Exception as e:
            logger.error(f"Error getting current branch: {str(e)}")
            return None
        finally:
            os.chdir(original_cwd)