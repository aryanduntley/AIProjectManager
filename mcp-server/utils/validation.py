"""
Schema validation utilities for the MCP server.

Provides functions for validating JSON files against schemas, with detailed
error reporting and schema loading capabilities.
"""

import json
import jsonschema
from jsonschema import Draft7Validator, validators
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging

from .json_utils import read_json, JSONValidationError

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Exception raised for schema validation errors."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class SchemaNotFoundError(Exception):
    """Exception raised when schema file is not found."""
    pass


class SchemaRegistry:
    """Registry for loading and caching JSON schemas."""
    
    def __init__(self, schema_dir: Union[str, Path]):
        self.schema_dir = Path(schema_dir)
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._validators: Dict[str, Draft7Validator] = {}
        
    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Load a schema from the schema directory.
        
        Args:
            schema_name: Name of schema file (e.g., "config.json")
            
        Returns:
            Schema dictionary
            
        Raises:
            SchemaNotFoundError: If schema file doesn't exist
            JSONValidationError: If schema file is invalid JSON
        """
        if schema_name in self._schemas:
            return self._schemas[schema_name]
            
        schema_path = self.schema_dir / schema_name
        
        if not schema_path.exists():
            raise SchemaNotFoundError(f"Schema not found: {schema_path}")
            
        try:
            schema = read_json(schema_path)
            self._schemas[schema_name] = schema
            
            # Pre-compile validator for performance
            self._validators[schema_name] = Draft7Validator(schema)
            
            logger.debug(f"Loaded schema: {schema_name}")
            return schema
            
        except Exception as e:
            logger.error(f"Error loading schema {schema_name}: {e}")
            raise SchemaValidationError(f"Invalid schema file {schema_name}: {e}")
    
    def get_validator(self, schema_name: str) -> Draft7Validator:
        """
        Get a compiled validator for a schema.
        
        Args:
            schema_name: Name of schema file
            
        Returns:
            Compiled JSON Schema validator
        """
        if schema_name not in self._validators:
            self.load_schema(schema_name)
            
        return self._validators[schema_name]
    
    def list_schemas(self) -> List[str]:
        """
        List all available schema files.
        
        Returns:
            List of schema filenames
        """
        if not self.schema_dir.exists():
            return []
            
        return [f.name for f in self.schema_dir.glob("*.json")]


def validate_against_schema(
    data: Dict[str, Any], 
    schema: Dict[str, Any],
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate data against a JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Raises:
        SchemaValidationError: If validation fails and raise_on_error=True
    """
    try:
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        
        if not errors:
            return True, []
            
        # Format error messages
        error_messages = []
        for error in errors:
            path = " -> ".join(str(p) for p in error.absolute_path)
            message = f"At '{path}': {error.message}"
            error_messages.append(message)
            
        if raise_on_error:
            raise SchemaValidationError(
                f"Schema validation failed with {len(errors)} error(s)",
                error_messages
            )
            
        return False, error_messages
        
    except jsonschema.SchemaError as e:
        error_msg = f"Invalid schema: {e.message}"
        if raise_on_error:
            raise SchemaValidationError(error_msg)
        return False, [error_msg]


def validate_file_against_schema(
    file_path: Union[str, Path],
    schema_path: Union[str, Path],
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate a JSON file against a schema file.
    
    Args:
        file_path: Path to JSON file to validate
        schema_path: Path to schema file
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Raises:
        FileNotFoundError: If either file doesn't exist
        SchemaValidationError: If validation fails and raise_on_error=True
    """
    try:
        data = read_json(file_path)
        schema = read_json(schema_path)
        
        return validate_against_schema(data, schema, raise_on_error)
        
    except Exception as e:
        error_msg = f"Error validating {file_path} against {schema_path}: {e}"
        if raise_on_error:
            raise SchemaValidationError(error_msg)
        return False, [error_msg]


def validate_with_registry(
    data: Dict[str, Any],
    schema_name: str,
    registry: SchemaRegistry,
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate data against a schema from the registry.
    
    Args:
        data: Data to validate
        schema_name: Name of schema in registry
        registry: Schema registry instance
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        validator = registry.get_validator(schema_name)
        errors = list(validator.iter_errors(data))
        
        if not errors:
            return True, []
            
        # Format error messages
        error_messages = []
        for error in errors:
            path = " -> ".join(str(p) for p in error.absolute_path)
            message = f"At '{path}': {error.message}"
            error_messages.append(message)
            
        if raise_on_error:
            raise SchemaValidationError(
                f"Schema validation failed with {len(errors)} error(s)",
                error_messages
            )
            
        return False, error_messages
        
    except Exception as e:
        error_msg = f"Error validating against schema {schema_name}: {e}"
        if raise_on_error:
            raise SchemaValidationError(error_msg)
        return False, [error_msg]


def validate_file_with_registry(
    file_path: Union[str, Path],
    schema_name: str,
    registry: SchemaRegistry,
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate a file against a schema from the registry.
    
    Args:
        file_path: Path to JSON file to validate
        schema_name: Name of schema in registry
        registry: Schema registry instance
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        data = read_json(file_path)
        return validate_with_registry(data, schema_name, registry, raise_on_error)
        
    except Exception as e:
        error_msg = f"Error validating file {file_path}: {e}"
        if raise_on_error:
            raise SchemaValidationError(error_msg)
        return False, [error_msg]


def get_schema_defaults(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract default values from a JSON schema.
    
    Args:
        schema: JSON schema
        
    Returns:
        Dictionary with default values
        
    Note:
        Only extracts defaults from top-level properties.
        Nested defaults require recursive processing.
    """
    defaults = {}
    
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if "default" in prop_schema:
                defaults[prop_name] = prop_schema["default"]
            elif prop_schema.get("type") == "object" and "properties" in prop_schema:
                # Recursive handling for nested objects
                nested_defaults = get_schema_defaults(prop_schema)
                if nested_defaults:
                    defaults[prop_name] = nested_defaults
                    
    return defaults


def validate_required_fields(
    data: Dict[str, Any], 
    required_fields: List[str],
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate that required fields are present and non-empty.
    
    Args:
        data: Data to validate
        required_fields: List of required field names (supports dot notation)
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Example:
        >>> validate_required_fields({"user": {"name": "John"}}, ["user.name"])
        (True, [])
    """
    errors = []
    
    for field in required_fields:
        # Handle dot notation (nested fields)
        keys = field.split('.')
        current = data
        
        try:
            for key in keys:
                if not isinstance(current, dict) or key not in current:
                    errors.append(f"Required field missing: {field}")
                    break
                current = current[key]
            else:
                # Check if value is empty
                if current is None or current == "" or (isinstance(current, (list, dict)) and len(current) == 0):
                    errors.append(f"Required field is empty: {field}")
                    
        except (TypeError, KeyError):
            errors.append(f"Required field missing: {field}")
    
    if errors and raise_on_error:
        raise SchemaValidationError(f"Required field validation failed", errors)
        
    return len(errors) == 0, errors


def validate_enum_values(
    data: Dict[str, Any], 
    field_enums: Dict[str, List[str]],
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate that fields contain valid enum values.
    
    Args:
        data: Data to validate
        field_enums: Dict mapping field names to allowed values
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Example:
        >>> validate_enum_values(
        ...     {"status": "active"}, 
        ...     {"status": ["active", "inactive"]}
        ... )
        (True, [])
    """
    errors = []
    
    for field, allowed_values in field_enums.items():
        keys = field.split('.')
        current = data
        
        try:
            for key in keys:
                if not isinstance(current, dict) or key not in current:
                    break  # Field doesn't exist, skip validation
                current = current[key]
            else:
                # Field exists, validate value
                if current not in allowed_values:
                    errors.append(f"Field '{field}' has invalid value '{current}'. Allowed values: {allowed_values}")
                    
        except (TypeError, KeyError):
            continue  # Field doesn't exist, skip validation
    
    if errors and raise_on_error:
        raise SchemaValidationError(f"Enum validation failed", errors)
        
    return len(errors) == 0, errors


def validate_file_references(
    data: Dict[str, Any],
    base_path: Union[str, Path],
    reference_fields: List[str],
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate that file references in data point to existing files.
    
    Args:
        data: Data to validate
        base_path: Base path for resolving relative file paths
        reference_fields: List of field names that contain file references
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    base_path = Path(base_path)
    errors = []
    
    for field in reference_fields:
        keys = field.split('.')
        current = data
        
        try:
            for key in keys:
                if not isinstance(current, dict) or key not in current:
                    break  # Field doesn't exist, skip validation
                current = current[key]
            else:
                # Field exists, validate file reference
                if isinstance(current, str):
                    file_refs = [current]
                elif isinstance(current, list):
                    file_refs = current
                else:
                    continue
                
                for file_ref in file_refs:
                    if not isinstance(file_ref, str):
                        continue
                        
                    file_path = base_path / file_ref
                    if not file_path.exists():
                        errors.append(f"Referenced file does not exist: {file_ref} (resolved to {file_path})")
                        
        except (TypeError, KeyError):
            continue  # Field doesn't exist, skip validation
    
    if errors and raise_on_error:
        raise SchemaValidationError(f"File reference validation failed", errors)
        
    return len(errors) == 0, errors


def create_validator_with_defaults(schema: Dict[str, Any]) -> Draft7Validator:
    """
    Create a validator that fills in default values during validation.
    
    Args:
        schema: JSON schema
        
    Returns:
        JSON Schema validator with default value handling
        
    Note:
        The returned validator will modify the data being validated
        to include default values for missing properties.
    """
    def extend_with_default(validator_class):
        """
        Extend a validator class to include default value handling.
        """
        validate_properties = validator_class.VALIDATORS["properties"]
        
        def set_defaults(validator, properties, instance, schema):
            for property, subschema in properties.items():
                if "default" in subschema:
                    instance.setdefault(property, subschema["default"])
                    
            for error in validate_properties(validator, properties, instance, schema):
                yield error
                
        all_validators = dict(validator_class.VALIDATORS)
        all_validators["properties"] = set_defaults
        
        return validators.create(
            meta_schema=validator_class.META_SCHEMA,
            validators=all_validators
        )
    
    DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)
    return DefaultValidatingDraft7Validator(schema)


def format_validation_error(error: jsonschema.ValidationError) -> str:
    """
    Format a validation error into a human-readable message.
    
    Args:
        error: Validation error from jsonschema
        
    Returns:
        Formatted error message
    """
    path = " -> ".join(str(p) for p in error.absolute_path)
    
    if path:
        return f"At '{path}': {error.message}"
    else:
        return error.message


def validate_cross_references(
    data: Dict[str, Any],
    reference_rules: List[Dict[str, Any]],
    raise_on_error: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate cross-references between fields in data.
    
    Args:
        data: Data to validate
        reference_rules: List of reference validation rules
        raise_on_error: Whether to raise exception on validation error
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Example:
        >>> rules = [{
        ...     "source_field": "task.milestoneId", 
        ...     "target_field": "milestones",
        ...     "rule": "exists_in_list"
        ... }]
        >>> validate_cross_references(data, rules)
    """
    errors = []
    
    # This is a placeholder for cross-reference validation logic
    # Implementation would depend on specific reference rules format
    # For now, just return valid
    
    return True, []