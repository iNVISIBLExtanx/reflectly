"""
Spark Service for Reflectly
Handles submitting and managing Spark jobs
"""
import os
import uuid
import subprocess
import logging
import json
import time
from urllib.parse import urlparse
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkService:
    def __init__(self, spark_master="spark://spark-master:7077", spark_submit_path="spark-submit"):
        """
        Initialize Spark configuration
        
        Args:
            spark_master (str): Spark master URL
            spark_submit_path (str): Path to spark-submit command
        """
        self.spark_master = spark_master
        self.spark_submit_path = spark_submit_path
        self.jobs = {}
        self._check_spark_connection()
        
    def _check_spark_connection(self):
        """Check if Spark master is reachable"""
        try:
            # Parse the Spark master URL to get host and port
            parsed_url = urlparse(self.spark_master)
            host = parsed_url.netloc.split(':')[0]
            port = parsed_url.netloc.split(':')[1]
            
            # Try to connect to Spark master UI
            url = f"http://{host}:8080/json/"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"Successfully connected to Spark master at {self.spark_master}")
                return True
            else:
                logger.warning(f"Spark master at {self.spark_master} returned status code {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Failed to connect to Spark master at {self.spark_master}: {e}")
            return False
            
    def submit_job(self, job_path, job_args=None, job_name=None, executor_memory="1g", executor_cores=1):
        """
        Submit a PySpark job to the Spark cluster
        
        Args:
            job_path (str): Path to the PySpark job script
            job_args (list): Arguments to pass to the job
            job_name (str): Name of the job
            executor_memory (str): Memory per executor
            executor_cores (int): Number of cores per executor
            
        Returns:
            str: Job ID if job was submitted successfully, None otherwise
        """
        if not os.path.exists(job_path):
            logger.error(f"Job script {job_path} not found")
            return None
            
        # Generate job ID and name
        job_id = str(uuid.uuid4())
        if not job_name:
            job_name = f"reflectly-{os.path.basename(job_path)}-{job_id[:8]}"
            
        # Build command
        cmd = [
            self.spark_submit_path,
            "--master", self.spark_master,
            "--name", job_name,
            "--executor-memory", executor_memory,
            "--executor-cores", str(executor_cores),
            job_path
        ]
        
        # Add job arguments if provided
        if job_args:
            cmd.extend(job_args)
            
        logger.info(f"Submitting Spark job: {' '.join(cmd)}")
        
        try:
            # Start job process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Store job information
            self.jobs[job_id] = {
                "id": job_id,
                "name": job_name,
                "path": job_path,
                "args": job_args,
                "process": process,
                "status": "running",
                "start_time": time.time(),
                "end_time": None,
                "exit_code": None,
                "stdout": [],
                "stderr": []
            }
            
            # Start threads to capture stdout and stderr
            self._start_output_capture(job_id)
            
            logger.info(f"Submitted Spark job with ID {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Failed to submit Spark job: {e}")
            return None
            
    def _start_output_capture(self, job_id):
        """
        Start threads to capture stdout and stderr from the job process
        
        Args:
            job_id (str): Job ID
        """
        import threading
        
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return
            
        def capture_output(stream, output_list):
            for line in stream:
                output_list.append(line.strip())
                
        # Start stdout thread
        stdout_thread = threading.Thread(
            target=capture_output,
            args=(job["process"].stdout, job["stdout"])
        )
        stdout_thread.daemon = True
        stdout_thread.start()
        
        # Start stderr thread
        stderr_thread = threading.Thread(
            target=capture_output,
            args=(job["process"].stderr, job["stderr"])
        )
        stderr_thread.daemon = True
        stderr_thread.start()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_job,
            args=(job_id,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
            
    def _monitor_job(self, job_id):
        """
        Monitor a job and update its status when it completes
        
        Args:
            job_id (str): Job ID
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return
            
        # Wait for process to complete
        exit_code = job["process"].wait()
        
        # Update job status
        job["status"] = "completed" if exit_code == 0 else "failed"
        job["exit_code"] = exit_code
        job["end_time"] = time.time()
        
        logger.info(f"Job {job_id} {job['status']} with exit code {exit_code}")
            
    def get_job_status(self, job_id):
        """
        Get the status of a submitted job
        
        Args:
            job_id (str): Job ID
            
        Returns:
            dict: Job status information
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return None
            
        # Create a copy of job info without the process object
        job_info = job.copy()
        job_info.pop("process", None)
        
        return job_info
        
    def get_all_jobs(self):
        """
        Get information about all jobs
        
        Returns:
            list: List of job information dictionaries
        """
        return [
            {k: v for k, v in job.items() if k != "process"}
            for job in self.jobs.values()
        ]
        
    def cancel_job(self, job_id):
        """
        Cancel a running job
        
        Args:
            job_id (str): Job ID
            
        Returns:
            bool: True if job was cancelled successfully, False otherwise
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return False
            
        if job["status"] != "running":
            logger.warning(f"Job {job_id} is not running (status: {job['status']})")
            return False
            
        try:
            job["process"].terminate()
            job["status"] = "cancelled"
            job["end_time"] = time.time()
            logger.info(f"Cancelled job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
