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
        ...     "rule": "exists_in_list",
        ...     "target_id_field": "id"
        ... }]
        >>> validate_cross_references(data, rules)
    """
    errors = []
    
    try:
        for rule in reference_rules:
            rule_type = rule.get("rule")
            source_field = rule.get("source_field")
            target_field = rule.get("target_field")
            
            if not all([rule_type, source_field, target_field]):
                errors.append(f"Invalid reference rule: missing required fields (rule, source_field, target_field)")
                continue
            
            # Get source value
            source_value = _get_nested_value(data, source_field)
            if source_value is None:
                # Source field doesn't exist - skip validation (might be optional)
                continue
            
            # Get target data
            target_data = _get_nested_value(data, target_field)
            if target_data is None:
                errors.append(f"Target field '{target_field}' not found for cross-reference validation")
                continue
            
            # Apply validation rule
            if rule_type == "exists_in_list":
                error = _validate_exists_in_list(source_value, target_data, rule, source_field, target_field)
                if error:
                    errors.append(error)
                    
            elif rule_type == "exists_in_dict":
                error = _validate_exists_in_dict(source_value, target_data, rule, source_field, target_field)
                if error:
                    errors.append(error)
                    
            elif rule_type == "unique_in_list":
                error = _validate_unique_in_list(source_value, target_data, rule, source_field, target_field)
                if error:
                    errors.append(error)
                    
            elif rule_type == "parent_child_relationship":
                error = _validate_parent_child_relationship(source_value, target_data, rule, source_field, target_field)
                if error:
                    errors.append(error)
                    
            elif rule_type == "conditional_required":
                error = _validate_conditional_required(data, rule, source_field, target_field)
                if error:
                    errors.append(error)
                    
            elif rule_type == "mutual_exclusion":
                error = _validate_mutual_exclusion(data, rule, source_field, target_field)
                if error:
                    errors.append(error)
                    
            else:
                errors.append(f"Unknown cross-reference rule type: {rule_type}")
    
    except Exception as e:
        errors.append(f"Error during cross-reference validation: {str(e)}")
    
    if errors and raise_on_error:
        raise SchemaValidationError(f"Cross-reference validation failed", errors)
        
    return len(errors) == 0, errors


def _get_nested_value(data: Dict[str, Any], field_path: str) -> Any:
    """Get value from nested dictionary using dot notation."""
    try:
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
                
        return current
    except (TypeError, ValueError, KeyError):
        return None


def _validate_exists_in_list(source_value: Any, target_list: List[Any], rule: Dict[str, Any], 
                           source_field: str, target_field: str) -> Optional[str]:
    """Validate that source_value exists in target_list."""
    if not isinstance(target_list, list):
        return f"Target field '{target_field}' is not a list for exists_in_list validation"
    
    target_id_field = rule.get("target_id_field", "id")
    
    # Handle different target list structures
    if target_list and isinstance(target_list[0], dict):
        # List of objects - check specified field
        target_values = [item.get(target_id_field) for item in target_list if isinstance(item, dict)]
    else:
        # List of primitives
        target_values = target_list
    
    if source_value not in target_values:
        return f"Value '{source_value}' in field '{source_field}' does not exist in '{target_field}'"
    
    return None


def _validate_exists_in_dict(source_value: Any, target_dict: Dict[str, Any], rule: Dict[str, Any],
                           source_field: str, target_field: str) -> Optional[str]:
    """Validate that source_value exists as a key in target_dict."""
    if not isinstance(target_dict, dict):
        return f"Target field '{target_field}' is not a dictionary for exists_in_dict validation"
    
    if source_value not in target_dict:
        return f"Key '{source_value}' in field '{source_field}' does not exist in '{target_field}'"
    
    return None


def _validate_unique_in_list(source_value: Any, target_list: List[Any], rule: Dict[str, Any],
                           source_field: str, target_field: str) -> Optional[str]:
    """Validate that source_value appears only once in target_list."""
    if not isinstance(target_list, list):
        return f"Target field '{target_field}' is not a list for unique_in_list validation"
    
    target_id_field = rule.get("target_id_field", "id")
    
    # Handle different target list structures
    if target_list and isinstance(target_list[0], dict):
        # List of objects - check specified field
        target_values = [item.get(target_id_field) for item in target_list if isinstance(item, dict)]
    else:
        # List of primitives
        target_values = target_list
    
    count = target_values.count(source_value)
    if count > 1:
        return f"Value '{source_value}' appears {count} times in '{target_field}', expected exactly 1"
    elif count == 0:
        return f"Value '{source_value}' in field '{source_field}' does not exist in '{target_field}'"
    
    return None


def _validate_parent_child_relationship(source_value: Any, target_data: Any, rule: Dict[str, Any],
                                      source_field: str, target_field: str) -> Optional[str]:
    """Validate parent-child relationship constraints."""
    parent_field = rule.get("parent_field", "parentId")
    child_field = rule.get("child_field", "id")
    
    if not isinstance(target_data, list):
        return f"Target field '{target_field}' must be a list for parent_child_relationship validation"
    
    # Find the source item
    source_item = None
    for item in target_data:
        if isinstance(item, dict) and item.get(child_field) == source_value:
            source_item = item
            break
    
    if not source_item:
        return f"Item with {child_field}='{source_value}' not found in '{target_field}'"
    
    # Check parent relationship
    parent_id = source_item.get(parent_field)
    if parent_id:
        # Verify parent exists
        parent_exists = any(
            isinstance(item, dict) and item.get(child_field) == parent_id 
            for item in target_data
        )
        if not parent_exists:
            return f"Parent '{parent_id}' for item '{source_value}' not found in '{target_field}'"
    
    return None


def _validate_conditional_required(data: Dict[str, Any], rule: Dict[str, Any],
                                 source_field: str, target_field: str) -> Optional[str]:
    """Validate conditional requirements between fields."""
    condition_field = rule.get("condition_field")
    condition_value = rule.get("condition_value")
    required_when = rule.get("required_when", True)
    
    if not condition_field:
        return "conditional_required rule missing 'condition_field'"
    
    condition_actual = _get_nested_value(data, condition_field)
    source_actual = _get_nested_value(data, source_field)
    
    # Check if condition is met
    condition_met = condition_actual == condition_value
    
    if required_when and condition_met and source_actual is None:
        return f"Field '{source_field}' is required when '{condition_field}' equals '{condition_value}'"
    elif not required_when and condition_met and source_actual is not None:
        return f"Field '{source_field}' must be empty when '{condition_field}' equals '{condition_value}'"
    
    return None


def _validate_mutual_exclusion(data: Dict[str, Any], rule: Dict[str, Any],
                             source_field: str, target_field: str) -> Optional[str]:
    """Validate that fields are mutually exclusive."""
    source_value = _get_nested_value(data, source_field)
    target_value = _get_nested_value(data, target_field)
    
    # Both fields have values - violation
    if source_value is not None and target_value is not None:
        return f"Fields '{source_field}' and '{target_field}' are mutually exclusive"
    
    # Check if at least one is required
    require_one = rule.get("require_one", False)
    if require_one and source_value is None and target_value is None:
        return f"At least one of '{source_field}' or '{target_field}' is required"
    
    return None