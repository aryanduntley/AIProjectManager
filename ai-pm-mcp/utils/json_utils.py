"""
JSON and JSONL utilities for the MCP server.

Provides functions for reading, writing, parsing, and validating JSON/JSONL files
with proper error handling and schema validation.
"""

import json
import jsonlines
from typing import Any, Dict, List, Optional, Union, Iterator
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class JSONLError(Exception):
    """Exception raised for JSONL-related errors."""
    pass


class JSONValidationError(Exception):
    """Exception raised for JSON validation errors."""
    pass


def read_json(file_path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        encoding: File encoding (default: utf-8)
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
        JSONValidationError: If file is empty or invalid
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
            
        content = file_path.read_text(encoding=encoding)
        
        if not content.strip():
            raise JSONValidationError(f"JSON file is empty: {file_path}")
            
        data = json.loads(content)
        
        if not isinstance(data, dict):
            raise JSONValidationError(f"JSON file must contain an object, got {type(data).__name__}: {file_path}")
            
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        raise


def write_json(
    file_path: Union[str, Path], 
    data: Dict[str, Any], 
    encoding: str = 'utf-8',
    indent: Optional[int] = 2,
    sort_keys: bool = False,
    ensure_ascii: bool = False
) -> None:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to write the JSON file
        data: Data to write
        encoding: File encoding (default: utf-8)
        indent: JSON indentation (None for compact, default: 2)
        sort_keys: Whether to sort dictionary keys
        ensure_ascii: Whether to escape non-ASCII characters
        
    Raises:
        TypeError: If data is not JSON serializable
        OSError: If file cannot be written
    """
    try:
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize to JSON
        json_content = json.dumps(
            data, 
            indent=indent, 
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii
        )
        
        # Write to file
        file_path.write_text(json_content, encoding=encoding)
        
        logger.debug(f"Successfully wrote JSON to {file_path}")
        
    except TypeError as e:
        logger.error(f"Data not JSON serializable for {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        raise


def read_jsonl(file_path: Union[str, Path], encoding: str = 'utf-8') -> List[Dict[str, Any]]:
    """
    Read and parse a JSONL file.
    
    Args:
        file_path: Path to the JSONL file
        encoding: File encoding (default: utf-8)
        
    Returns:
        List of parsed JSON objects
        
    Raises:
        FileNotFoundError: If file doesn't exist
        JSONLError: If file contains invalid JSONL
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {file_path}")
            
        data = []
        
        with jsonlines.open(file_path, mode='r', encoding=encoding) as reader:
            for line_num, obj in enumerate(reader, 1):
                if not isinstance(obj, dict):
                    raise JSONLError(f"JSONL line {line_num} must be an object, got {type(obj).__name__}: {file_path}")
                data.append(obj)
                
        return data
        
    except jsonlines.InvalidLineError as e:
        logger.error(f"Invalid JSONL in file {file_path}: {e}")
        raise JSONLError(f"Invalid JSONL format: {e}")
    except Exception as e:
        logger.error(f"Error reading JSONL file {file_path}: {e}")
        raise


def write_jsonl(
    file_path: Union[str, Path], 
    data: List[Dict[str, Any]], 
    encoding: str = 'utf-8',
    mode: str = 'w'
) -> None:
    """
    Write data to a JSONL file.
    
    Args:
        file_path: Path to write the JSONL file
        data: List of dictionaries to write
        encoding: File encoding (default: utf-8)
        mode: Write mode ('w' for overwrite, 'a' for append)
        
    Raises:
        TypeError: If data contains non-serializable objects
        OSError: If file cannot be written
        JSONLError: If data is not a list of dictionaries
    """
    try:
        file_path = Path(file_path)
        
        if not isinstance(data, list):
            raise JSONLError(f"Data must be a list, got {type(data).__name__}")
            
        # Validate all items are dictionaries
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise JSONLError(f"Item {i} must be a dictionary, got {type(item).__name__}")
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSONL
        with jsonlines.open(file_path, mode=mode, encoding=encoding) as writer:
            for item in data:
                writer.write(item)
                
        logger.debug(f"Successfully wrote {len(data)} items to JSONL file {file_path}")
        
    except Exception as e:
        logger.error(f"Error writing JSONL file {file_path}: {e}")
        raise


def append_jsonl(file_path: Union[str, Path], item: Dict[str, Any], encoding: str = 'utf-8') -> None:
    """
    Append a single item to a JSONL file.
    
    Args:
        file_path: Path to the JSONL file
        item: Dictionary to append
        encoding: File encoding (default: utf-8)
        
    Raises:
        TypeError: If item is not JSON serializable
        OSError: If file cannot be written
        JSONLError: If item is not a dictionary
    """
    try:
        if not isinstance(item, dict):
            raise JSONLError(f"Item must be a dictionary, got {type(item).__name__}")
            
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL
        with jsonlines.open(file_path, mode='a', encoding=encoding) as writer:
            writer.write(item)
            
        logger.debug(f"Successfully appended item to JSONL file {file_path}")
        
    except Exception as e:
        logger.error(f"Error appending to JSONL file {file_path}: {e}")
        raise


def iterate_jsonl(file_path: Union[str, Path], encoding: str = 'utf-8') -> Iterator[Dict[str, Any]]:
    """
    Iterate over a JSONL file without loading all data into memory.
    
    Args:
        file_path: Path to the JSONL file
        encoding: File encoding (default: utf-8)
        
    Yields:
        Dict[str, Any]: Each JSON object in the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        JSONLError: If file contains invalid JSONL
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {file_path}")
            
        with jsonlines.open(file_path, mode='r', encoding=encoding) as reader:
            for line_num, obj in enumerate(reader, 1):
                if not isinstance(obj, dict):
                    raise JSONLError(f"JSONL line {line_num} must be an object, got {type(obj).__name__}: {file_path}")
                yield obj
                
    except jsonlines.InvalidLineError as e:
        logger.error(f"Invalid JSONL in file {file_path}: {e}")
        raise JSONLError(f"Invalid JSONL format: {e}")
    except Exception as e:
        logger.error(f"Error reading JSONL file {file_path}: {e}")
        raise


def merge_json_objects(base: Dict[str, Any], update: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
    """
    Merge two JSON objects.
    
    Args:
        base: Base JSON object
        update: Object with updates to merge
        deep: Whether to perform deep merge (default: True)
        
    Returns:
        Merged JSON object
        
    Note:
        - If deep=True, nested dictionaries are merged recursively
        - If deep=False, top-level keys from update override base
        - Lists are replaced, not merged
    """
    if not deep:
        result = base.copy()
        result.update(update)
        return result
    
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json_objects(result[key], value, deep=True)
        else:
            result[key] = value
            
    return result


def minify_json(data: Dict[str, Any]) -> str:
    """
    Convert JSON object to minified JSON string.
    
    Args:
        data: JSON object to minify
        
    Returns:
        Minified JSON string
        
    Raises:
        TypeError: If data is not JSON serializable
    """
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)


def prettify_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Convert JSON object to pretty-formatted JSON string.
    
    Args:
        data: JSON object to format
        indent: Indentation spaces (default: 2)
        
    Returns:
        Pretty-formatted JSON string
        
    Raises:
        TypeError: If data is not JSON serializable
    """
    return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True)


def validate_json_structure(data: Any, expected_type: type = dict) -> bool:
    """
    Validate basic JSON structure.
    
    Args:
        data: Data to validate
        expected_type: Expected root type (default: dict)
        
    Returns:
        True if structure is valid
        
    Raises:
        JSONValidationError: If structure is invalid
    """
    if not isinstance(data, expected_type):
        raise JSONValidationError(f"Expected {expected_type.__name__}, got {type(data).__name__}")
        
    return True


def safe_json_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get a nested value from JSON object using dot notation.
    
    Args:
        data: JSON object
        key_path: Dot-separated key path (e.g., "user.profile.name")
        default: Default value if key not found
        
    Returns:
        Value at key path or default
        
    Example:
        >>> data = {"user": {"profile": {"name": "John"}}}
        >>> safe_json_get(data, "user.profile.name")
        "John"
        >>> safe_json_get(data, "user.profile.age", 0)
        0
    """
    try:
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    except Exception:
        return default


def file_size_bytes(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    return file_path.stat().st_size


def parse_size_string(size_str: str) -> int:
    """
    Parse size string (e.g., "1MB", "500KB") to bytes.
    
    Args:
        size_str: Size string with unit (B, KB, MB, GB)
        
    Returns:
        Size in bytes
        
    Raises:
        ValueError: If size string format is invalid
        
    Example:
        >>> parse_size_string("1MB")
        1048576
        >>> parse_size_string("500KB")
        512000
    """
    size_str = size_str.strip().upper()
    
    # Extract number and unit
    import re
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str)
    
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
        
    number, unit = match.groups()
    number = float(number)
    
    # Convert to bytes
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
        '': 1  # Default to bytes
    }
    
    if unit not in multipliers:
        raise ValueError(f"Unknown size unit: {unit}")
        
    return int(number * multipliers[unit])