#!/usr/bin/env python3
"""
Quick test script to validate API connection and configuration.
"""

import sys
import os
from pathlib import Path
import unittest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.config import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL, SYSTEM_PROMPT
from core.api_client import LLMClient


class TestConfiguration(unittest.TestCase):
    def test_configuration(self):
        """Test if configuration is properly set."""
        print("🔍 Checking configuration...")
        
        checks = [
            ("API Key", bool(OPENAI_API_KEY) and OPENAI_API_KEY != "your_api_key_here"),
            ("Base URL", bool(OPENAI_BASE_URL)),
            ("Model", bool(LLM_MODEL)),
            ("System Prompt", bool(SYSTEM_PROMPT)),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}: {'OK' if passed else 'MISSING'}")
            if not passed:
                all_passed = False
        
        self.assertTrue(all_passed, "Configuration checks failed.")


class TestAPIConnection(unittest.TestCase):
    def test_api_connection(self):
        """Test API connection."""
        print("\n🌐 Testing API connection...")
        
        try:
            client = LLMClient()
            print("  ✓ Client initialized")
            
            self.assertTrue(client.validate_connection(), "API connection failed.")
        except Exception as e:
            self.fail(f"Error: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM CLI Tool - Configuration Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test configuration
    results.append(("Configuration", TestConfiguration().test_configuration()))
    
    # Test API connection
    results.append(("API Connection", TestAPIConnection().test_api_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✅ All tests passed! You're ready to use the CLI tool.")
        print("Run: python main.py")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        print("Instructions:")
        print("1. Edit .env file with valid API credentials")
        print("2. Make sure OPENAI_API_KEY is not 'your_api_key_here'")
        print("3. Verify your API key is correct and has sufficient quota")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    unittest.main()
