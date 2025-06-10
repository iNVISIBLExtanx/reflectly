"""
HDFS Service for Reflectly
Handles reading from and writing to HDFS
"""
import os
import tempfile
import logging
import subprocess
import json
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HDFSService:
    def __init__(self, namenode="namenode:9000", hdfs_bin="hdfs"):
        """
        Initialize HDFS configuration
        
        Args:
            namenode (str): HDFS namenode host:port
            hdfs_bin (str): Path to HDFS binary
        """
        self.namenode = namenode
        self.hdfs_bin = hdfs_bin
        self.hdfs_url = f"hdfs://{namenode}"
        self._check_hdfs_connection()
        
    def _check_hdfs_connection(self):
        """Check if HDFS is reachable"""
        try:
            result = self._run_hdfs_command(["dfs", "-ls", "/"])
            if result["exit_code"] == 0:
                logger.info(f"Successfully connected to HDFS at {self.hdfs_url}")
                return True
            else:
                logger.warning(f"HDFS at {self.hdfs_url} returned error: {result['stderr']}")
                return False
        except Exception as e:
            logger.warning(f"Failed to connect to HDFS at {self.hdfs_url}: {e}")
            return False
            
    def _run_hdfs_command(self, args):
        """
        Run an HDFS command
        
        Args:
            args (list): Command arguments
            
        Returns:
            dict: Command result with stdout, stderr, and exit_code
        """
        cmd = [self.hdfs_bin] + args
        logger.debug(f"Running HDFS command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            result = {
                "stdout": stdout.strip(),
                "stderr": stderr.strip(),
                "exit_code": exit_code
            }
            
            if exit_code != 0:
                logger.error(f"HDFS command failed with exit code {exit_code}: {stderr.strip()}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to run HDFS command: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }
            
    def read_file(self, hdfs_path):
        """
        Read a file from HDFS
        
        Args:
            hdfs_path (str): HDFS path to the file
            
        Returns:
            str: File content if successful, None otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Reading file from HDFS: {hdfs_path}")
        
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Run HDFS command to get the file
            result = self._run_hdfs_command(["dfs", "-get", path, temp_path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to read file from HDFS: {result['stderr']}")
                return None
                
            # Read the content from the temporary file
            with open(temp_path, 'r') as f:
                content = f.read()
                
            return content
        except Exception as e:
            logger.error(f"Failed to read file from HDFS: {e}")
            return None
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def write_file(self, content, hdfs_path):
        """
        Write content to a file in HDFS
        
        Args:
            content (str): Content to write
            hdfs_path (str): HDFS path to write to
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Writing file to HDFS: {hdfs_path}")
        
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
            
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(path)
            if parent_dir:
                mkdir_result = self._run_hdfs_command(["dfs", "-mkdir", "-p", parent_dir])
                if mkdir_result["exit_code"] != 0:
                    logger.error(f"Failed to create parent directory in HDFS: {mkdir_result['stderr']}")
                    return False
                    
            # Run HDFS command to put the file
            result = self._run_hdfs_command(["dfs", "-put", "-f", temp_path, path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to write file to HDFS: {result['stderr']}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to write file to HDFS: {e}")
            return False
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def write_local_file(self, local_path, hdfs_path):
        """
        Write a local file to HDFS
        
        Args:
            local_path (str): Path to local file
            hdfs_path (str): HDFS path to write to
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Writing local file {local_path} to HDFS: {hdfs_path}")
        
        try:
            # Check if local file exists
            if not os.path.exists(local_path):
                logger.error(f"Local file {local_path} not found")
                return False
                
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(path)
            if parent_dir:
                mkdir_result = self._run_hdfs_command(["dfs", "-mkdir", "-p", parent_dir])
                if mkdir_result["exit_code"] != 0:
                    logger.error(f"Failed to create parent directory in HDFS: {mkdir_result['stderr']}")
                    return False
                    
            # Run HDFS command to put the file
            result = self._run_hdfs_command(["dfs", "-put", "-f", local_path, path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to write local file to HDFS: {result['stderr']}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to write local file to HDFS: {e}")
            return False
            
    def list_directory(self, hdfs_path):
        """
        List files in an HDFS directory
        
        Args:
            hdfs_path (str): HDFS path to list
            
        Returns:
            list: List of file information dictionaries
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Listing directory in HDFS: {hdfs_path}")
        
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Run HDFS command to list the directory
            result = self._run_hdfs_command(["dfs", "-ls", "-R", path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to list directory in HDFS: {result['stderr']}")
                return []
                
            # Parse the output
            files = []
            for line in result["stdout"].split("\n"):
                if not line or line.startswith("Found"):
                    continue
                    
                parts = line.split()
                if len(parts) < 8:
                    continue
                    
                file_info = {
                    "permissions": parts[0],
                    "replication": parts[1],
                    "owner": parts[2],
                    "group": parts[3],
                    "size": parts[4],
                    "modified_date": parts[5],
                    "modified_time": parts[6],
                    "path": parts[7]
                }
                
                files.append(file_info)
                
            return files
        except Exception as e:
            logger.error(f"Failed to list directory in HDFS: {e}")
            return []
            
    def delete_file(self, hdfs_path, recursive=False):
        """
        Delete a file or directory from HDFS
        
        Args:
            hdfs_path (str): HDFS path to delete
            recursive (bool): Whether to delete recursively
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Deleting {'recursively ' if recursive else ''}from HDFS: {hdfs_path}")
        
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Run HDFS command to delete the file or directory
            cmd = ["dfs", "-rm"]
            if recursive:
                cmd.append("-r")
            cmd.append(path)
            
            result = self._run_hdfs_command(cmd)
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to delete from HDFS: {result['stderr']}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to delete from HDFS: {e}")
            return False
