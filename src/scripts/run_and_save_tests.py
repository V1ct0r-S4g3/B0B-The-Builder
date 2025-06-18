"""Run tests and save output to a file."""
import sys
import io
import contextlib
from pathlib import Path

def capture_output():
    """Capture stdout and stderr."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            # Import and run the test module
            from tests import test_military_manager_extended
            print("Successfully imported test module")
            
            # Get all test functions
            test_functions = [
                (test_military_manager_extended.test_strategy_management, "Strategy Management"),
                (test_military_manager_extended.test_unit_production, "Unit Production"),
                (test_military_manager_extended.test_combat_management, "Combat Management"),
                (test_military_manager_extended.test_build_order_execution, "Build Order Execution"),
                (test_military_manager_extended.test_upgrade_management, "Upgrade Management"),
                (test_military_manager_extended.test_emergency_supply, "Emergency Supply"),
                (test_military_manager_extended.test_army_composition, "Army Composition"),
            ]
            
            # Run tests
            print("\nRunning tests...")
            for test_func, name in test_functions:
                print(f"\nRunning test: {name}")
                if asyncio.iscoroutinefunction(test_func):
                    asyncio.run(test_func)
                else:
                    test_func()
                print(f"✅ {name} - PASSED")
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    return output.getvalue()

if __name__ == "__main__":
    import asyncio
    
    # Add project root to Python path
    project_root = str(Path(__file__).parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Run tests and capture output
    output = capture_output()
    
    # Save output to file
    output_file = Path("test_output.txt")
    output_file.write_text(output, encoding="utf-8")
    print(f"\nTest output saved to: {output_file.absolute()}")
    
    # Also print to console
    print("\nTest Output:")
    print("="*80)
    print(output)
    print("="*80)
