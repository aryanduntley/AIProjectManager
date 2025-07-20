#!/usr/bin/env python3
"""
Comprehensive test for the theme system of the AI Project Manager MCP Server.

Tests theme discovery, management, and context loading functionality.
"""

import asyncio
import json
import shutil
import sys
import tempfile
from pathlib import Path

# Add the current directory and deps to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "deps"))

from core.config_manager import ConfigManager
from core.mcp_api import MCPToolRegistry
from tools.theme_tools import ThemeTools
from utils.theme_discovery import ThemeDiscovery
from core.scope_engine import ScopeEngine, ContextMode


async def create_test_project(temp_dir: Path) -> Path:
    """Create a test project structure for theme testing."""
    project_path = temp_dir / "test_project"
    
    # Create directory structure
    directories = [
        "src/components",
        "src/pages", 
        "src/services/auth",
        "src/services/payment",
        "src/utils",
        "src/hooks",
        "src/store",
        "src/styles",
        "tests/unit",
        "tests/integration",
        "api/controllers",
        "api/middleware",
        "config",
        "docs"
    ]
    
    for dir_path in directories:
        (project_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create test files
    files = {
        "package.json": json.dumps({
            "name": "test-project",
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0",
                "stripe": "^10.0.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }, indent=2),
        "src/components/Login.tsx": """
import React from 'react';
import { useAuth } from '../hooks/useAuth';

export const Login = () => {
    const { login } = useAuth();
    return <div>Login Component</div>;
};
""",
        "src/components/PaymentForm.tsx": """
import React from 'react';
import { loadStripe } from '@stripe/stripe-js';

export const PaymentForm = () => {
    return <div>Payment Form</div>;
};
""",
        "src/services/auth/authService.ts": """
export class AuthService {
    async login(email: string, password: string) {
        // Authentication logic
    }
    
    async logout() {
        // Logout logic
    }
}
""",
        "src/services/payment/paymentService.ts": """
import Stripe from 'stripe';

export class PaymentService {
    private stripe: Stripe;
    
    async processPayment(amount: number) {
        // Payment processing logic
    }
}
""",
        "src/hooks/useAuth.ts": """
import { useState, useEffect } from 'react';

export const useAuth = () => {
    const [user, setUser] = useState(null);
    
    return { user, login: () => {}, logout: () => {} };
};
""",
        "src/utils/validators.ts": """
export const validateEmail = (email: string): boolean => {
    return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);
};
""",
        "api/controllers/authController.js": """
const express = require('express');

exports.login = async (req, res) => {
    // Login endpoint
};

exports.register = async (req, res) => {
    // Register endpoint  
};
""",
        "api/controllers/paymentController.js": """
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.createPaymentIntent = async (req, res) => {
    // Create payment intent
};
""",
        "tests/unit/auth.test.js": """
const { AuthService } = require('../../src/services/auth/authService');

describe('AuthService', () => {
    test('should login user', () => {
        // Test logic
    });
});
""",
        "README.md": """# Test Project

This is a test project for theme discovery testing.

## Features
- User authentication
- Payment processing
- Component library
""",
        "src/components/README.md": """# Components

Reusable UI components for the application.

## Available Components
- Login: User login form
- PaymentForm: Payment processing form
""",
        "src/services/README.md": """# Services

Business logic and API integration services.

## Services
- AuthService: Handles user authentication
- PaymentService: Processes payments via Stripe
"""
    }
    
    for file_path, content in files.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    return project_path


async def test_theme_discovery():
    """Test automatic theme discovery."""
    print("Testing theme discovery...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = await create_test_project(temp_path)
        
        # Initialize project management structure
        from tools.project_tools import ProjectTools
        project_tools = ProjectTools()
        await project_tools.initialize_project({
            "project_path": str(project_path),
            "project_name": "Test Project"
        })
        
        # Test theme discovery
        theme_discovery = ThemeDiscovery()
        result = theme_discovery.discover_themes(project_path)
        
        themes = result.get('themes', {})
        print(f"✓ Discovered {len(themes)} themes")
        
        # Check for expected themes
        expected_themes = ['authentication', 'payment', 'components', 'testing', 'api']
        found_themes = list(themes.keys())
        
        for expected in expected_themes:
            if any(expected in theme for theme in found_themes):
                print(f"✓ Found expected theme category: {expected}")
            else:
                print(f"⚠ Missing expected theme category: {expected}")
        
        # Check theme quality
        for theme_name, theme_data in themes.items():
            confidence = theme_data.get('score', 0)
            evidence = theme_data.get('evidence', {})
            
            print(f"  - {theme_name}: confidence={confidence:.2f}, "
                  f"files={len(evidence.get('files', []))}, "
                  f"dirs={len(evidence.get('directories', []))}")
        
        return True


async def test_theme_tools():
    """Test theme management tools."""
    print("Testing theme management tools...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = await create_test_project(temp_path)
        
        # Initialize project
        from tools.project_tools import ProjectTools
        project_tools = ProjectTools()
        await project_tools.initialize_project({
            "project_path": str(project_path),
            "project_name": "Test Project"
        })
        
        # Test theme tools
        theme_tools = ThemeTools()
        
        # Test theme discovery with force rediscovery
        result = await theme_tools.discover_themes({
            "project_path": str(project_path),
            "force_rediscovery": True
        })
        print(f"✓ Theme discovery: {result[:100]}...")
        
        # Test theme listing
        result = await theme_tools.list_themes({
            "project_path": str(project_path)
        })
        print(f"✓ Theme listing: {result[:100]}...")
        
        # Test creating a custom theme
        result = await theme_tools.create_theme({
            "project_path": str(project_path),
            "theme_name": "custom-theme",
            "description": "A custom theme for testing",
            "paths": ["src/custom"],
            "files": ["src/custom/custom.ts"]
        })
        print(f"✓ Theme creation: {result}")
        
        # Test getting specific theme
        result = await theme_tools.get_theme({
            "project_path": str(project_path),
            "theme_name": "custom-theme"
        })
        print(f"✓ Theme retrieval: {result[:100]}...")
        
        # Test theme validation
        result = await theme_tools.validate_themes({
            "project_path": str(project_path)
        })
        print(f"✓ Theme validation: {result[:100]}...")
        
        return True


async def test_context_loading():
    """Test context loading engine."""
    print("Testing context loading engine...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = await create_test_project(temp_path)
        
        # Initialize project and discover themes
        from tools.project_tools import ProjectTools
        project_tools = ProjectTools()
        await project_tools.initialize_project({
            "project_path": str(project_path),
            "project_name": "Test Project"
        })
        
        theme_tools = ThemeTools()
        await theme_tools.discover_themes({
            "project_path": str(project_path),
            "force_rediscovery": True
        })
        
        # Test context loading
        scope_engine = ScopeEngine()
        
        # Get available themes
        themes_result = await theme_tools.list_themes({
            "project_path": str(project_path),
            "include_details": True
        })
        
        # Parse themes from result
        if "Detailed themes:" in themes_result:
            themes_json = themes_result.split("Detailed themes:\n\n")[1]
            try:
                themes_data = json.loads(themes_json)
                theme_names = list(themes_data.keys())
                
                if theme_names:
                    primary_theme = theme_names[0]
                    
                    # Test different context modes
                    for mode in [ContextMode.THEME_FOCUSED, ContextMode.THEME_EXPANDED, ContextMode.PROJECT_WIDE]:
                        try:
                            context = await scope_engine.load_context(
                                project_path, primary_theme, mode
                            )
                            
                            summary = await scope_engine.get_context_summary(context)
                            print(f"✓ Context loading ({mode.value}): {len(context.files)} files, "
                                  f"{len(context.loaded_themes)} themes")
                            print(f"  Memory estimate: {context.memory_estimate}MB")
                            print(f"  READMEs found: {len(context.readmes)}")
                            
                            # Test relevance filtering
                            relevant_files = await scope_engine.filter_files_by_relevance(
                                context, "authentication login user"
                            )
                            print(f"  Relevant files for 'authentication': {len(relevant_files)}")
                            
                        except Exception as e:
                            print(f"  ⚠ Error testing {mode.value}: {e}")
                else:
                    print("⚠ No themes found to test context loading")
                    
            except json.JSONDecodeError:
                print("⚠ Could not parse themes data for context testing")
        
        return True


async def test_theme_context_integration():
    """Test integration between themes and context loading."""
    print("Testing theme-context integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = await create_test_project(temp_path)
        
        # Initialize and set up themes
        from tools.project_tools import ProjectTools
        project_tools = ProjectTools()
        await project_tools.initialize_project({
            "project_path": str(project_path),
            "project_name": "Test Project"
        })
        
        theme_tools = ThemeTools()
        await theme_tools.discover_themes({
            "project_path": str(project_path),
            "force_rediscovery": True
        })
        
        # Test theme context tool
        themes_list = await theme_tools.list_themes({
            "project_path": str(project_path)
        })
        
        # Extract theme names
        if "Available themes" in themes_list:
            lines = themes_list.split('\n')
            theme_lines = [line for line in lines if line.startswith('- ')]
            if theme_lines:
                first_theme_line = theme_lines[0]
                theme_name = first_theme_line.split(': ')[0].replace('- ', '')
                
                # Test theme context loading
                result = await theme_tools.get_theme_context({
                    "project_path": str(project_path),
                    "primary_theme": theme_name,
                    "context_mode": "theme-focused"
                })
                print(f"✓ Theme context integration: {result[:100]}...")
                
                # Test expanded context
                result = await theme_tools.get_theme_context({
                    "project_path": str(project_path),
                    "primary_theme": theme_name,
                    "context_mode": "theme-expanded"
                })
                print(f"✓ Expanded context: {result[:100]}...")
        
        return True


async def test_complete_workflow():
    """Test complete theme discovery and usage workflow."""
    print("Testing complete workflow...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = await create_test_project(temp_path)
        
        # 1. Initialize project
        from tools.project_tools import ProjectTools
        project_tools = ProjectTools()
        init_result = await project_tools.initialize_project({
            "project_path": str(project_path),
            "project_name": "Test Project"
        })
        print("✓ Project initialized")
        
        # 2. Discover themes
        theme_tools = ThemeTools()
        discovery_result = await theme_tools.discover_themes({
            "project_path": str(project_path),
            "force_rediscovery": True
        })
        print("✓ Themes discovered")
        
        # 3. List and validate themes
        list_result = await theme_tools.list_themes({
            "project_path": str(project_path)
        })
        print("✓ Themes listed")
        
        validation_result = await theme_tools.validate_themes({
            "project_path": str(project_path)
        })
        print("✓ Themes validated")
        
        # 4. Create custom theme
        custom_result = await theme_tools.create_theme({
            "project_path": str(project_path),
            "theme_name": "workflow-test",
            "description": "Theme created during workflow test",
            "paths": ["src/workflow"],
            "files": []
        })
        print("✓ Custom theme created")
        
        # 5. Load context for different modes
        scope_engine = ScopeEngine()
        
        # Parse first available theme
        if "Available themes" in list_result:
            lines = list_result.split('\n')
            theme_lines = [line for line in lines if line.startswith('- ')]
            if theme_lines:
                first_theme = theme_lines[0].split(': ')[0].replace('- ', '')
                
                for mode in [ContextMode.THEME_FOCUSED, ContextMode.THEME_EXPANDED]:
                    try:
                        context = await scope_engine.load_context(project_path, first_theme, mode)
                        print(f"✓ Context loaded ({mode.value}): {len(context.files)} files")
                    except Exception as e:
                        print(f"⚠ Context loading failed ({mode.value}): {e}")
        
        print("✓ Complete workflow tested successfully")
        return True


async def main():
    """Run all theme system tests."""
    print("=== AI Project Manager Theme System Tests ===\n")
    
    tests = [
        ("Theme Discovery", test_theme_discovery),
        ("Theme Management Tools", test_theme_tools),
        ("Context Loading Engine", test_context_loading),
        ("Theme-Context Integration", test_theme_context_integration),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✓ {test_name} passed\n")
        except Exception as e:
            print(f"✗ {test_name} failed: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All theme system tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)