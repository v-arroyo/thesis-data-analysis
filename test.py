# debug_env.py - Run this from your subfolder
import os
from pathlib import Path
from dotenv import load_dotenv

print("🔍 DEBUGGING .env LOADING")
print("=" * 60)

# Method 1: Find project root
current_file = Path(__file__).resolve()
print(f"Script location: {current_file}")

# Look for .git folder
project_root = None
for parent in current_file.parents:
    git_path = parent / '.git'
    if git_path.exists() and git_path.is_dir():
        project_root = parent
        print(f"✅ Found project root (has .git): {project_root}")
        break

if not project_root:
    print("❌ No .git folder found in parent directories")
    # Fallback: use parent of parent (assuming chapters/subfolder structure)
    project_root = current_file.parent.parent
    print(f"⚠️  Using fallback: {project_root}")

# Check for .env
env_path = project_root / '.env'
print(f"\n.env path: {env_path}")
print(f".env exists: {env_path.exists()}")

if env_path.exists():
    print(f".env size: {env_path.stat().st_size} bytes")
    
    # Show .env contents
    print("\n--- .env FILE CONTENTS ---")
    with open(env_path, 'r') as f:
        for i, line in enumerate(f, 1):
            print(f"{i:2}: {line.rstrip()}")
    print("--- END CONTENTS ---")
    
    # Try loading with dotenv
    try:
        from dotenv import load_dotenv
        
        # Load .env
        print("\n🔧 Loading .env with python-dotenv...")
        success = load_dotenv(dotenv_path=env_path)
        print(f"load_dotenv() returned: {success}")
        
        # Check ALL environment variables starting with DB_
        print("\n📋 Checking environment variables:")
        all_env_vars = dict(os.environ)
        db_vars = {k: v for k, v in all_env_vars.items() if 'DB' in k.upper()}
        
        if db_vars:
            for key, value in sorted(db_vars.items()):
                masked = '******' if 'PASSWORD' in key.upper() else value
                print(f"  {key}: {masked}")
        else:
            print("  ❌ No DB_* environment variables found!")
            
        # Check specific variables
        print("\n🔍 Checking specific variables:")
        test_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_HOST', 'DB_PORT']
        for var in test_vars:
            value = os.getenv(var)
            if value:
                masked = '******' if 'PASSWORD' in var else value
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ❌ {var}: NOT SET or None")
                
    except ImportError:
        print("\n❌ python-dotenv is not installed!")
        print("Run: pip install python-dotenv")
        
else:
    print("\n❌ .env file not found at the expected location!")
    print(f"\nLooking for .env in other locations:")
    locations = []
    
    # Check common locations
    for parent in current_file.parents:
        test_path = parent / '.env'
        if test_path.exists():
            locations.append(str(test_path))
    
    if locations:
        print("Found .env files at:")
        for loc in locations:
            print(f"  • {loc}")
    else:
        print("No .env files found anywhere!")

print("\n" + "=" * 60)