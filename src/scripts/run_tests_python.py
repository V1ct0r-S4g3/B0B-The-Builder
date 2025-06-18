"""Run tests and capture output to a file."""
import sys
import subprocess
import datetime
import os

def run_test(test_name, test_path):
    """Run a single test and return the result."""
    print(f"\n[RUNNING] {test_name}...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "-s"],
        capture_output=True,
        text=True
    )
    return result

def main():
    """Run all tests and save detailed output."""
    # Create output directory if it doesn't exist
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a timestamp for the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_results_{timestamp}.txt")
    
    # List of tests to run
    tests = [
        ("Hello Test", "tests/test_hello.py"),
        ("MilitaryManager Simple Test", "tests/test_military_simple.py"),
        ("MilitaryManager Extended Tests", "tests/test_military_manager_extended.py")
    ]
    
    print(f"Running tests and saving output to: {output_file}")
    print("=" * 60)
    
    all_output = []
    
    for test_name, test_path in tests:
        # Run the test
        result = run_test(test_name, test_path)
        
        # Format the output
        test_output = f"\n{'='*60}\n"
        test_output += f"TEST: {test_name}\n"
        test_output += f"PATH: {test_path}\n"
        test_output += f"EXIT CODE: {result.returncode}\n"
        test_output += f"{'='*60}\n"
        test_output += result.stdout
        
        if result.stderr:
            test_output += "\nERRORS:\n"
            test_output += result.stderr
        
        test_output += f"\n{'='*60}\n"
        
        # Print a summary
        status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
        print(f"{status}: {test_name}")
        
        # Save the output
        all_output.append(test_output)
    
    # Write all output to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_output))
    
    print(f"\nTest output saved to: {os.path.abspath(output_file)}")
    
    # Save to file
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
    
    print("Output saved to test_output.txt")
    
    # Run the military manager test
    print("\nRunning MilitaryManager test...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_military_simple.py", "-v", "-s"],
        capture_output=True,
        text=True
    )
    
    # Print the output
    print("\n=== Test Output ===")
    print(result.stdout)
    print("=== End of Output ===\n")
    
    # Append to file
    with open("test_output.txt", "a", encoding="utf-8") as f:
        f.write("\n" + "="*50 + "\n")
        f.write("MilitaryManager Test Output\n")
        f.write("="*50 + "\n\n")
        f.write(result.stdout)
    
    print("Output appended to test_output.txt")

if __name__ == "__main__":
    main()
