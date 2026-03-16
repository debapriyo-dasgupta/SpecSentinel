"""
SpecSentinel AI Agent Setup Script
Quick setup and verification for AI-powered analysis with multi-LLM support
"""

import os
import sys
from pathlib import Path

def check_llm_packages():
    """Check which LLM packages are installed."""
    packages = {}
    
    # Check OpenAI
    try:
        import openai
        packages['openai'] = True
        print("✅ OpenAI package installed")
    except ImportError:
        packages['openai'] = False
        print("❌ OpenAI package not installed")
    
    # Check Anthropic
    try:
        import anthropic
        packages['anthropic'] = True
        print("✅ Anthropic package installed")
    except ImportError:
        packages['anthropic'] = False
        print("❌ Anthropic package not installed")
    
    # Check WatsonX
    try:
        import ibm_watsonx_ai
        packages['watsonx'] = True
        print("✅ IBM WatsonX.ai package installed")
    except ImportError:
        packages['watsonx'] = False
        print("❌ IBM WatsonX.ai package not installed")
    
    # Check Google
    try:
        import google.generativeai
        packages['google'] = True
        print("✅ Google Generative AI package installed")
    except ImportError:
        packages['google'] = False
        print("❌ Google Generative AI package not installed")
    
    return packages

def check_api_keys():
    """Check which API keys are configured."""
    keys = {}
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        masked = openai_key[:7] + "..." + openai_key[-4:] if len(openai_key) > 11 else "***"
        print(f"✅ OpenAI API key configured: {masked}")
        keys['openai'] = True
    else:
        print("❌ OpenAI API key not found")
        keys['openai'] = False
    
    # Check Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        masked = anthropic_key[:7] + "..." + anthropic_key[-4:] if len(anthropic_key) > 11 else "***"
        print(f"✅ Anthropic API key configured: {masked}")
        keys['anthropic'] = True
    else:
        print("❌ Anthropic API key not found")
        keys['anthropic'] = False
    
    # Check WatsonX
    watsonx_key = os.getenv("WATSONX_API_KEY")
    watsonx_project = os.getenv("WATSONX_PROJECT_ID")
    if watsonx_key and watsonx_project:
        masked_key = watsonx_key[:7] + "..." + watsonx_key[-4:] if len(watsonx_key) > 11 else "***"
        masked_proj = watsonx_project[:8] + "..." if len(watsonx_project) > 8 else "***"
        print(f"✅ WatsonX API key configured: {masked_key}")
        print(f"✅ WatsonX Project ID configured: {masked_proj}")
        keys['watsonx'] = True
    else:
        print("❌ WatsonX credentials not found (need both API key and Project ID)")
        keys['watsonx'] = False
    
    # Check Google
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        masked = google_key[:7] + "..." + google_key[-4:] if len(google_key) > 11 else "***"
        print(f"✅ Google API key configured: {masked}")
        keys['google'] = True
    else:
        print("❌ Google API key not found")
        keys['google'] = False
    
    return keys

def test_ai_agent():
    """Test Universal AI Agent functionality."""
    try:
        from src.engine.ai_agent_universal import UniversalAIAgent, get_available_providers
        
        available = get_available_providers()
        if not available:
            print("❌ No LLM providers available (missing API keys)")
            return False, None
        
        print(f"✅ Available providers: {', '.join(available)}")
        
        # Try to initialize
        agent = UniversalAIAgent()
        if agent.is_available():
            info = agent.get_provider_info()
            print(f"✅ AI Agent initialized with {info['provider']} ({info['model']})")
            return True, info['provider']
        else:
            print("❌ AI Agent initialization failed")
            return False, None
        
    except Exception as e:
        print(f"❌ AI Agent test failed: {e}")
        return False, None

def main():
    """Main setup verification."""
    print("=" * 70)
    print("  SpecSentinel Multi-LLM Setup Verification")
    print("=" * 70)
    print()
    
    # Check 1: LLM Packages
    print("1. Checking LLM packages...")
    packages = check_llm_packages()
    print()
    
    any_package = any(packages.values())
    if not any_package:
        print("📦 Install at least one LLM package:")
        print("   pip install -r requirements.txt")
        print()
        print("   Or install individually:")
        print("   pip install openai>=1.12.0              # OpenAI")
        print("   pip install anthropic>=0.18.0           # Anthropic Claude")
        print("   pip install ibm-watsonx-ai>=1.0.0       # IBM WatsonX.ai")
        print("   pip install google-generativeai>=0.3.0  # Google Gemini")
        print()
    
    # Check 2: API Keys
    print("2. Checking API keys...")
    keys = check_api_keys()
    print()
    
    any_key = any(keys.values())
    if not any_key:
        print("🔑 Set at least one API key:")
        print()
        print("   OpenAI:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   Get key: https://platform.openai.com/api-keys")
        print()
        print("   Anthropic:")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   Get key: https://console.anthropic.com/")
        print()
        print("   IBM WatsonX.ai:")
        print("   export WATSONX_API_KEY='your-key'")
        print("   export WATSONX_PROJECT_ID='your-project-id'")
        print("   Get key: https://cloud.ibm.com/")
        print("   See docs/WATSONX_SETUP.md for detailed setup")
        print()
        print("   Google Gemini:")
        print("   export GOOGLE_API_KEY='your-key'")
        print("   Get key: https://makersuite.google.com/app/apikey")
        print()
    
    # Check 3: AI Agent
    if any_package and any_key:
        print("3. Testing AI Agent...")
        agent_ok, provider = test_ai_agent()
        print()
        
        if agent_ok:
            print("=" * 70)
            print("  ✅ AI Agent Setup Complete!")
            print("=" * 70)
            print()
            print(f"Active Provider: {provider}")
            print()
            print("You can now use AI-powered analysis:")
            print("  - AI-generated explanations")
            print("  - Auto-generated fix code")
            print("  - Risk assessments")
            print("  - Priority recommendations")
            print()
            print("Start the server and analyze your API specs!")
            print()
            print("For more information:")
            print("  - Multi-LLM Setup: docs/MULTI_LLM_SETUP.md")
            print("  - WatsonX Setup: docs/WATSONX_SETUP.md")
            print()
            return 0
    
    print("=" * 70)
    print("  ⚠️  AI Agent Setup Incomplete")
    print("=" * 70)
    print()
    print("Complete the steps above to enable AI features.")
    print("SpecSentinel will work without AI, but with limited insights.")
    print()
    print("For detailed setup instructions, see:")
    print("  - docs/MULTI_LLM_SETUP.md")
    print("  - docs/WATSONX_SETUP.md")
    print("  - docs/AI_AGENT_GUIDE.md")
    print()
    return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
