"""Test script to verify module imports."""
import sys
import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_imports')

def test_import(module_name):
    """Test importing a module and log the result."""
    try:
        __import__(module_name)
        logger.info(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error importing {module_name}: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing module imports...")
    
    # Core Python modules
    core_modules = ['os', 'sys', 'logging', 'asyncio', 'pathlib', 'typing']
    
    # SC2 and related modules
    sc2_modules = [
        'sc2',
        'sc2.bot_ai',
        'sc2.main',
        'sc2.data',
        'sc2.player',
        'sc2.protocol',
    ]
    
    # Our modules
    our_modules = [
        'bot.main',
        'managers.head_manager',
        'managers.economy_manager',
        'managers.military_manager',
    ]
    
    # Test all modules
    all_imports = core_modules + sc2_modules + our_modules
    results = {mod: test_import(mod) for mod in all_imports}
    
    # Print summary
    success = sum(1 for r in results.values() if r)
    total = len(results)
    
    logger.info("\n" + "="*50)
    logger.info(f"Import test summary: {success}/{total} successful imports")
    logger.info("="*50)
    
    if success < total:
        failed = [mod for mod, result in results.items() if not result]
        logger.warning(f"Failed to import: {', '.join(failed)}")
        sys.exit(1)
