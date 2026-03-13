"""
SpecSentinel AI Agent Setup Script
Quick setup and verification for AI-powered analysis
"""

import os
import sys
from pathlib import Path

def check_openai_installed():
    """Check if OpenAI package is installed."""
    try:
        import openai
        print("✅ OpenAI package installed")
        return True
    except ImportError:
        print("❌ OpenAI package not installed")
        return False

def check_api_key():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
        print(f"✅ OpenAI API key configured: {masked_key}")
        return True
    else:
        print("❌ OpenAI API key not found")
        return False

def test_ai_agent():
    """Test AI Agent functionality."""
    try:
        from src.engine.ai_agent import SpecSentinelAIAgent, is_ai_agent_available
        
        if not is_ai_agent_available():
            print("❌ AI Agent not available (missing API key)")
            return False
        
        print("✅ AI Agent available")
        
        # Try to initialize
        agent = SpecSentinelAIAgent()
        print(f"✅ AI Agent initialized with model: {agent.model}")
        return True
        
    except Exception as e:
        print(f"❌ AI Agent test failed: {e}")
        return False

def main():
    """Main setup verification."""
    print("=" * 60)
    print("  SpecSentinel AI Agent Setup Verification")
    print("=" * 60)
    print()
    
    # Check 1: OpenAI package
    print("1. Checking OpenAI package...")
    openai_ok = check_openai_installed()
    print()
    
    if not openai_ok:
        print("📦 Install OpenAI package:")
        print("   pip install openai>=1.12.0")
        print()
    
    # Check 2: API Key
    print("2. Checking OpenAI API key...")
    key_ok = check_api_key()
    print()
    
    if not key_ok:
        print("🔑 Set your OpenAI API key:")
        print()
        print("   Windows PowerShell:")
        print("   $env:OPENAI_API_KEY = 'sk-your-api-key-here'")
        print()
        print("   Linux/Mac:")
        print("   export OPENAI_API_KEY='sk-your-api-key-here'")
        print()
        print("   Get your API key from: https://platform.openai.com/api-keys")
        print()
    
    # Check 3: AI Agent
    if openai_ok and key_ok:
        print("3. Testing AI Agent...")
        agent_ok = test_ai_agent()
        print()
        
        if agent_ok:
            print("=" * 60)
            print("  ✅ AI Agent Setup Complete!")
            print("=" * 60)
            print()
            print("You can now use AI-powered analysis:")
            print("  - AI-generated explanations")
            print("  - Auto-generated fix code")
            print("  - Risk assessments")
            print("  - Priority recommendations")
            print()
            print("Start the server and analyze your API specs!")
            print()
            return 0
    
    print("=" * 60)
    print("  ⚠️  AI Agent Setup Incomplete")
    print("=" * 60)
    print()
    print("Complete the steps above to enable AI features.")
    print("SpecSentinel will work without AI, but with limited insights.")
    print()
    print("For detailed setup instructions, see:")
    print("  docs/AI_AGENT_GUIDE.md")
    print()
    return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
