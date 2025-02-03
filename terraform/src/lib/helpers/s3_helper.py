from concurrent.futures import ThreadPoolExecutor
import threading
from typing import Optional, List, Dict, Union
import boto3
import os
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
from pathlib import Path

class DownloadStats:
    def __init__(self):
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self._lock = threading.Lock()
    
    def increment_downloaded(self):
        with self._lock:
            self.downloaded += 1
    
    def increment_skipped(self):
        with self._lock:
            self.skipped += 1
    
    def increment_failed(self):
        with self._lock:
            self.failed += 1

def download_from_s3_prefix(
    bucket_name: str,
    local_directory: str,
    prefix: Optional[str] = None,
    include_prefixes: Optional[List[str]] = None,
    exclude_prefixes: Optional[List[str]] = None,
    profile_name: Optional[str] = None,
    region: str = "us-west-2",
    max_workers: int = 10,
    overwrite: bool = True,
    logger: Optional[logging.Logger] = None
) -> Dict[str, int]:
    """
    Download all files from an S3 prefix to a local directory with parallel processing.
    
    Args:
        bucket_name (str): Name of the S3 bucket
        prefix (str): S3 prefix/folder path
        local_directory (str): Local directory path to save files
        include_prefixes (List[str]): List of specific prefixes to include (if None, includes all)
        exclude_prefixes (List[str]): List of prefixes to exclude from download
        profile_name (Optional[str]): AWS profile name to use
        region (str): AWS region name
        max_workers (int): Number of concurrent downloads
        overwrite (bool): Whether to overwrite existing files
        logger (Optional[logging.Logger]): Custom logger instance
    
    Returns:
        Dict[str, int]: Statistics of the download operation
    """
    # Use provided logger or create a default one
    log = logger or logging.getLogger(__name__)
    
    stats = DownloadStats()
    exclude_prefixes = exclude_prefixes or []
    include_prefixes = include_prefixes or []
    # Ensure prefix is an empty string if None
    prefix = prefix or ""

    def should_process_object(object_key: str, prefix: str) -> bool:
        """
        Determine if object should be processed based on include/exclude rules.
        
        Args:
            object_key (str): The S3 object key to check
            prefix (str): S3 prefix/folder path
            
        Returns:
            bool: True if object should be processed, False otherwise
            
        Logic:
            1. If include_prefixes is specified:
            - Object must match one of the include prefixes
            - AND must not match any exclude prefixes
            2. If include_prefixes is not specified:
            - Object must not match any exclude prefixes
        """
        # First check include prefixes if specified
        if include_prefixes:
            if prefix:
                included = any(object_key.startswith(f"{prefix.rstrip('/')}/{inc.strip('/')}") 
                        for inc in include_prefixes)
            else:
                included = any(object_key.startswith(f"{inc.strip('/')}") 
                        for inc in include_prefixes)
            if not included:
                return False
        
        # Then check exclude prefixes
        if exclude_prefixes:
            if prefix:
                excluded = any(object_key.startswith(f"{prefix.rstrip('/')}/{ex.strip('/')}") 
                        for ex in exclude_prefixes)
            else:
                excluded = any(object_key.startswith(f"{ex.strip('/')}") 
                        for ex in exclude_prefixes)
            if excluded:
                return False
        
        # If we get here:
        # - Either no include_prefixes were specified or the object matched one
        # - AND either no exclude_prefixes were specified or the object matched none
        return True

    def download_file(obj: Dict) -> None:
        with semaphore:  # Use semaphore to control concurrency
            try:
                if not should_process_object(obj['Key'], prefix):
                    log.debug(f"Skipping file: {obj['Key']}")
                    stats.increment_skipped()
                    return

                relative_path = obj['Key'][len(prefix):].lstrip('/') if prefix else obj['Key']
                local_file_path = os.path.join(local_directory, relative_path)

                if not overwrite and os.path.exists(local_file_path):
                    log.debug(f"Skipping existing file: {local_file_path}")
                    stats.increment_skipped()
                    return

                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                s3_client.download_file(bucket_name, obj['Key'], local_file_path)
                stats.increment_downloaded()
                log.debug(f"Downloaded: {obj['Key']}")

            except Exception as e:
                log.error(f"Failed to download {obj['Key']}: {str(e)}")
                stats.increment_failed()

    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        config = Config(
            max_pool_connections=max_workers,
            retries={'max_attempts': 3},
            connect_timeout=5,
            read_timeout=60
        )
        s3_client = session.client('s3', config=config)
        semaphore = threading.Semaphore(max_workers)

        os.makedirs(local_directory, exist_ok=True)

        paginator = s3_client.get_paginator('list_objects_v2')
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                if 'Contents' not in page:
                    continue
                
                # Submit all files in the page for parallel download
                futures = list(executor.map(download_file, page['Contents']))
            
            executor.shutdown(wait=True)  # Wait for all threads to complete

        log.info(f"""Download Summary:
        - Files downloaded: {stats.downloaded}
        - Files skipped: {stats.skipped}
        - Files failed: {stats.failed}
        - From: s3://{bucket_name}/{prefix}
        - To: {local_directory}
        - Included prefixes: {', '.join(include_prefixes) if include_prefixes else 'All'}
        - Excluded prefixes: {', '.join(exclude_prefixes) if exclude_prefixes else 'None'}
        """)

        return {
            "downloaded": stats.downloaded,
            "skipped": stats.skipped,
            "failed": stats.failed
        }

    except ClientError as e:
        log.error(f"AWS Error: {str(e)}")
        raise
    except Exception as e:
        log.error(f"Error: {str(e)}")
        raise
    finally:
        # Ensure the S3 client session is closed
        if 's3_client' in locals():
            s3_client._endpoint.http_session.close()

class UploadStats:
    def __init__(self):
        self.uploaded = 0
        self.skipped = 0
        self.failed = 0
        self._lock = threading.Lock()
    
    def increment_uploaded(self):
        with self._lock:
            self.uploaded += 1
    
    def increment_skipped(self):
        with self._lock:
            self.skipped += 1
    
    def increment_failed(self):
        with self._lock:
            self.failed += 1

def upload_to_s3_prefix(
    bucket_name: str,
    local_directory: Union[str, Path],
    s3_prefix: str = "",
    exclude_patterns: Optional[List[str]] = None,
    profile_name: Optional[str] = None,
    region: str = "us-west-2",
    max_workers: int = 10,
    overwrite: bool = True,
    logger: Optional[logging.Logger] = None
) -> Dict[str, int]:
    """
    Upload files from a local directory to S3 with parallel processing.
    
    Args:
        bucket_name (str): Name of the S3 bucket
        local_directory (Union[str, Path]): Local directory path to upload from
        s3_prefix (str): S3 prefix/folder path to upload to
        exclude_patterns (List[str]): List of file patterns to exclude (supports wildcards)
        profile_name (Optional[str]): AWS profile name to use
        region (str): AWS region name
        max_workers (int): Number of concurrent uploads
        overwrite (bool): Whether to overwrite existing files in S3
        logger (Optional[logging.Logger]): Custom logger instance
    
    Returns:
        Dict[str, int]: Statistics of the upload operation
    """
    import fnmatch
    
    # Use provided logger or create a default one
    log = logger or logging.getLogger(__name__)
    
    stats = UploadStats()
    exclude_patterns = exclude_patterns or []
    local_directory = Path(local_directory)
    
    def should_exclude_file(file_path: str) -> bool:
        """Check if file matches any exclude pattern"""
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns)

    def get_s3_key(file_path: Path) -> str:
        """Generate S3 key for the file"""
        relative_path = str(file_path.relative_to(local_directory))
        return f"{s3_prefix.rstrip('/')}/{relative_path}".lstrip('/')

    def file_exists_in_s3(s3_key: str) -> bool:
        """Check if file exists in S3"""
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def upload_file(file_path: Path) -> None:
        with semaphore:  # Use semaphore to control concurrency
            try:
                if should_exclude_file(str(file_path)):
                    log.debug(f"Skipping excluded file: {file_path}")
                    stats.increment_skipped()
                    return

                s3_key = get_s3_key(file_path)

                # Check if file exists and skip if overwrite is False
                if not overwrite and file_exists_in_s3(s3_key):
                    log.debug(f"Skipping existing file in S3: {s3_key}")
                    stats.increment_skipped()
                    return

                # Upload file with progress callback
                file_size = os.path.getsize(file_path)
                
                def upload_progress(bytes_transferred):
                    percentage = (bytes_transferred * 100) / file_size
                    log.debug(f"Uploading {s3_key}: {percentage:.1f}%")

                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key,
                    Callback=upload_progress if file_size > 1024*1024 else None  # Only show progress for files > 1MB
                )
                
                stats.increment_uploaded()
                log.debug(f"Uploaded: {file_path} -> s3://{bucket_name}/{s3_key}")

            except Exception as e:
                log.error(f"Failed to upload {file_path}: {str(e)}")
                stats.increment_failed()

    try:
        # Validate local directory
        if not local_directory.exists():
            raise ValueError(f"Local directory does not exist: {local_directory}")

        # Initialize S3 client
        session = boto3.Session(profile_name=profile_name, region_name=region)
        config = Config(
            max_pool_connections=max_workers * 2,
            retries={'max_attempts': 3},
            connect_timeout=5,
            read_timeout=60,
            tcp_keepalive=True
        )
        s3_client = session.client('s3', config=config)
        semaphore = threading.Semaphore(max_workers)

        # Get list of files to upload
        files_to_upload = [
            f for f in local_directory.rglob('*') 
            if f.is_file() and not should_exclude_file(str(f))
        ]

        if not files_to_upload:
            log.warning(f"No files found to upload in {local_directory}")
            return {
                "uploaded": 0,
                "skipped": 0,
                "failed": 0
            }

        # Upload files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            try:
                futures = list(executor.map(upload_file, files_to_upload))
            finally:
                executor.shutdown(wait=True)  # Wait for all threads to complete
                s3_client._endpoint.http_session.close()

        log.info(f"""Upload Summary:
        - Files uploaded: {stats.uploaded}
        - Files skipped: {stats.skipped}
        - Files failed: {stats.failed}
        - From: {local_directory}
        - To: s3://{bucket_name}/{s3_prefix}
        - Excluded patterns: {', '.join(exclude_patterns) if exclude_patterns else 'None'}
        """)

        return {
            "uploaded": stats.uploaded,
            "skipped": stats.skipped,
            "failed": stats.failed
        }

    except ClientError as e:
        log.error(f"AWS Error: {str(e)}")
        raise
    except Exception as e:
        log.error(f"Error: {str(e)}")
        raise
    finally:
        # Ensure the S3 client session is closed
        if 's3_client' in locals():
            s3_client._endpoint.http_session.close()