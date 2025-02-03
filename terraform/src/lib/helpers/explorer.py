import os
import logging
from pathlib import Path
from enum import StrEnum
from string import Template

class FileMarker(StrEnum):
    CREATED = "created.marker"
    UPDATED = "updated.marker"
    DELETED = "deleted.marker"
    REVIEWED = "reviewed.marker"
    CLEANED = "cleaned.marker"
    SUMMARY = "summary.marker"
    COPIED = "copied.marker"
    FINISHED = "finished.marker"
    SKIP = "skip.marker"

TEMPLATE_FILE_FORMAT = Template("""
---
page_title: "{{.Name}} {{.Type}} - {{.ProviderName}}"
subcategory: ""
description: |-
{{ .Description | plainmarkdown | trimspace | prefixlines "  " }}
---

# {{.Name}} ({{.Type}})

{{ .Description | trimspace }}

## Example Usage

$summary_text

~> This example is generated by LLM using Amazon Bedrock and validated using terraform validate, apply and destroy. While we strive for accuracy and quality, please note that the information provided may not be entirely error-free or up-to-date. We recommend independently verifying the content.

{{ tffile (printf "examples/resources/%s/main.tf" .Name)}}

{{ .SchemaMarkdown | trimspace }}
{{- if .HasImport }}

## Import

Import is supported using the following syntax:

{{ codefile "shell" .ImportFile }}

{{- end }}
""")

def find_dirs_without_tf_files(base_path: str, logger: logging.Logger):
    
    # Convert the base path to a Path object
    base_dir = Path(base_path)
    
    # List to store directories without .tf files
    dirs_without_tf = []
    
    # Check if the base directory exists
    if not base_dir.exists():
        logger.info(f"Directory {base_path} does not exist")
        return dirs_without_tf
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_dir):
        # Convert current directory path to Path object
        current_dir = Path(root)
        
        # Skip the base directory itself
        if current_dir == base_dir:
            continue
            
        # Check if there are any .tf files in the current directory
        tf_files = list(current_dir.glob('*.tf'))
        
        # If no .tf files found, add to our list
        if not tf_files:
            # Store relative path instead of absolute path
            relative_path = os.path.relpath(current_dir, base_dir)
            # Normalize the path separator and check the prefix
            normalized_path = os.path.normpath(relative_path).replace(os.sep, '/')
            if normalized_path.startswith('examples/resources/'):
                dirs_without_tf.append(relative_path)

    return dirs_without_tf

def list_subdirectories(parent_dir: str, logger: logging.Logger) -> list:
    """
    List all subdirectories under the given parent directory.

    Args:
        parent_dir (str): Path to the parent directory

    Returns:
        list: List of subdirectories

    Raises:
        ValueError: If parent_dir is not a valid directory
    """
    # Check if parent_dir is a valid directory
    if not os.path.isdir(parent_dir):
        logger.error(f"{parent_dir} is not a valid directory")
        raise ValueError(f"{parent_dir} is not a valid directory")

    # List to store subdirectories
    subdirectories = []

    # Walk through the parent directory
    for root, dirs, _ in os.walk(parent_dir):
        # Skip the parent directory itself
        if root == parent_dir:
            continue

        # Add each subdirectory to the list
        for dir_name in dirs:
            subdirectories.append(os.path.join(root, dir_name))

    return subdirectories

def check_if_dir_contains_example(dir_path: str) -> bool:
    """
    Check if a directory contains an example file.

    Args:
        dir_path (str): Path to the directory to check

    Returns:
        bool: True if the directory contains an example file, False otherwise
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        return False

    # Check if the directory contains an example file
    for file in os.listdir(dir_path):
        if file.endswith('.tf'):
            return True

    return False

def check_if_dir_contains_marker(dir_path: str, marker_type: str = FileMarker.REVIEWED) -> bool:
    """
    Check if a directory contains a marker file.

    Args:
        dir_path (str): Path to the directory to check
        marker_type (str): Type of marker file to delete

    Returns:
        bool: True if the directory contains a marker file, False otherwise
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        return False

    # Check if the directory contains a marker file
    for file in os.listdir(dir_path):
        if file == marker_type:
            return True

    return False

def check_if_dir_contains_statefile(dir_path: str) -> bool:
    """
    Check if a directory contains a state file.

    Args:
        dir_path (str): Path to the directory to check

    Returns:
        bool: True if the directory contains a state file, False otherwise
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        return False

    # Check if the directory contains a state file
    for file in os.listdir(dir_path):
        if file.endswith('.tfstate'):
            return True

    return False

def create_directory(base_path: str, directory_name: str, logger: logging.Logger) -> str:
    """
    Create a new directory under the base path.
    
    Args:
        base_path (str): The base directory path
        directory_name (str): Name of the directory to create
        
    Returns:
        str: Path of the created directory
        
    Raises:
        ValueError: If input parameters are invalid
        OSError: If directory creation fails
    """
    # Input validation
    if not base_path or not directory_name:
        raise ValueError("Both base_path and directory_name must be provided")
    
    # Check if base path exists
    if not Path(base_path).exists():
        raise ValueError(f"Base path does not exist: {base_path}")
        
    try:
        full_path = os.path.join(base_path, directory_name)
        dir_path = Path(full_path)
        
        # Skip if directory already exists
        if dir_path.exists():
            return str(dir_path)
            
        # Create directory and any necessary parent directories
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return str(dir_path)
    except OSError as e:
        logger.warning(f"Failed to create directory {full_path}: {e}")
        raise OSError(f"Failed to create directory {full_path}") from e

def delete_directory(dir_path: str, logger: logging.Logger) -> bool:
    """
    Delete a directory and all its contents.

    Args:
        dir_path (str): Path to the directory to delete

    Returns:
        bool: True if the directory was deleted, False otherwise
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        logger.error(f"Directory {dir_path} does not exist")
        return False

    try:
        # Delete the directory and all its contents
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(dir_path)
        logger.info(f"Directory {dir_path} deleted successfully")
        return True
    except OSError as e:
        logger.warning(f"Unable to delete directory {dir_path}: {e}")
        return False
    
def create_marker(dir_path: str, marker_type: str, logger: logging.Logger) -> bool:
    """
    Create a marker file in the specified directory.

    Args:
        dir_path (str): Path to the directory to create the marker file in
        marker_type (str): Type of marker file to create

    Returns:
        bool: True if the marker file was created, False otherwise
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        logger.error(f"Directory {dir_path} does not exist")
        return False

    # Check if the directory already contains the marker file
    marker_file = os.path.join(dir_path, marker_type)
    if os.path.isfile(marker_file):
        logger.warning(f"Marker file {marker_file} already exists")
        return False

    # Create the marker file
    try:
        Path(marker_file).touch()
        logger.info(f"Marker file {marker_file} created successfully")
        return True
    except OSError as e:
        logger.error(f"Error creating marker file {marker_file}: {e}")
        return False

def delete_marker(dir_path: str, marker_type: str = FileMarker.REVIEWED) -> bool:
    """
    Delete a marker file in the specified directory.

    Args:
        dir_path (str): Path to the directory containing the marker file
        marker_type (str): Type of marker file to delete

    Returns:
        bool: True if the marker file was deleted, False otherwise
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        return False

    # Check if the directory contains the marker file
    marker_file = os.path.join(dir_path, marker_type)
    if os.path.isfile(marker_file):
        try:
            os.remove(marker_file)
            return True
        except OSError as e:
            print(f"Error deleting marker file {marker_file}: {e}")
            return False

    return False

def create_template(resource_name: str, summary_text: str, directory_path: str, logger: logging.Logger, replace: bool = False) -> str:
    """
    Create a template file and store at the given file path.

    Args:
        title (str): Title of the example
        summary (str): Summary of the example
        file_path (str): Path to the file to create the template for

    Returns:
        str: Path to the created template file
    """

    try:
        # Create directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)
        
        file_path = os.path.join(directory_path, resource_name) + '.md.tmpl'

        # Check if the destination file exists
        if os.path.isfile(file_path) and not replace:
            logger.error(f"Destination file {file_path} already exists")
            return False

        # Create the template file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(TEMPLATE_FILE_FORMAT.substitute(
                summary_text=summary_text,
            ))
        logger.info(f"File {file_path} created successfully")
        return file_path
        
    except OSError as e:
        logger.error(f"Error creating directory or file at {file_path}: {e}")
        return False
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating template {file_path}: {e}")
        return False

def copy_file(source_file: str, destination_file: str, logger: logging.Logger, replace: bool = False,) -> bool:
    """
    Copy a file from source to destination.

    Args:
        source_file (str): Path to the source file
        destination_file (str): Path to the destination file

    Returns:
        bool: True if the file was copied successfully, False otherwise
    """
    # Check if source file exists
    if not os.path.isfile(source_file):
        logger.error(f"Source file {source_file} does not exist")
        return False

    # Check if destination file already exists
    if os.path.isfile(destination_file) and not replace:
        logger.error(f"Destination file {destination_file} already exists")
        return False

    try:
        # Copy the file, create dir if not exist
        destination_file=Path(destination_file)
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        with open(source_file, 'r', encoding='utf-8') as src, open(destination_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        logger.info(f"File {source_file} copied to {destination_file}")
        return True
    except IOError as e:
        logger.error(f"Error copying file {source_file} to {destination_file}: {e}")
        return False

def read_text_file(file_path: str, logger: logging.Logger) -> str:
    """
    Read the content of a text file.

    Args:
        file_path (str): Path to the text file

    Returns:
        str: Content of the text file
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        logger.error(f"File {file_path} does not exist")
        return ""

    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except UnicodeDecodeError as e:
        logger.error(f"Error decoding file {file_path} as UTF-8: {e}")
        return ""
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def check_file_size_with_units(file_path: str, max_size: float, unit: str = 'MB') -> bool:
    """
    Check if a file size is within the specified limit with unit support.

    Args:
        file_path (str): Path to the file to check
        max_size (float): Maximum allowed size in specified unit
        unit (str): Size unit ('B', 'KB', 'MB', 'GB', 'TB')

    Returns:
        bool: True if file size is within limit, False otherwise
    """
    # Unit conversion mapping
    unit_map = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            return False
            
        # Validate unit
        unit = unit.upper()
        if unit not in unit_map:
            raise ValueError(f"Invalid unit. Must be one of {', '.join(unit_map.keys())}")
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Convert max size to bytes
        max_size_bytes = max_size * unit_map[unit]
        
        # Compare with max size
        return file_size <= max_size_bytes
        
    except OSError as e:
        print(f"Error checking file size: {e}")
        return False