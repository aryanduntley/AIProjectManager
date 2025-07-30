#!/usr/bin/env python3
"""Debug theme discovery."""

import sys
import tempfile
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "deps"))

from .utils.theme_discovery import ThemeDiscovery

# Create simple test project
with tempfile.TemporaryDirectory() as temp_dir:
    project_path = Path(temp_dir) / "test"
    
    # Create auth-related structure
    (project_path / "src/auth").mkdir(parents=True)
    (project_path / "src/auth/login.js").write_text("const login = () => {};")
    (project_path / "src/components").mkdir(parents=True)
    (project_path / "src/components/LoginForm.jsx").write_text("import React from 'react';")
    
    # Debug structure analysis first
    from utils.file_utils import FileAnalyzer
    analyzer = FileAnalyzer()
    structure = analyzer.analyze_project_structure(project_path)
    
    print("Project structure:")
    print(f"  Directories: {structure.get('directories', {})}")
    print(f"  Files: {len(structure.get('files', []))}")
    print(f"  Keywords: {structure.get('keywords', {})}")
    
    # Test specific theme scoring
    discovery = ThemeDiscovery()
    
    # Test authentication theme scoring
    auth_config = discovery.theme_categories['functional_domains']['authentication']
    auth_score = discovery._calculate_theme_score(auth_config, structure)
    print(f"\nAuthentication theme score: {auth_score:.3f}")
    
    # Test components theme scoring  
    comp_config = discovery.theme_categories['user_interface']['components']
    comp_score = discovery._calculate_theme_score(comp_config, structure)
    print(f"Components theme score: {comp_score:.3f}")
    
    # Run full discovery
    result = discovery.discover_themes(project_path)
    
    print(f"\nThemes found: {len(result.get('themes', {}))}")
    for name, data in result.get('themes', {}).items():
        print(f"  {name}: score={data.get('score', 0):.3f}")
        print(f"    evidence: {data.get('evidence', {})}")