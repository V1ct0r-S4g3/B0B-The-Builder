"""Run MilitaryManager tests and capture output to a file."""
import sys
import subprocess
from datetime import datetime

def run_test(test_name, test_path):
    """Run a test and return the output."""
    print(f"Running {test_name}...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "-s"],
        capture_output=True,
        text=True
    )
    return result

def main():
    """Run tests and save output to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_military_{timestamp}.txt"
    
    print(f"Running MilitaryManager tests. Output will be saved to {output_file}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Test Run: {timestamp}\n")
        f.write("=" * 40 + "\n\n")
        
        # Run the simple test
        result = run_test("hello test", "tests/test_hello.py")
        f.write("=== Hello Test ===\n")
        f.write(f"Return code: {result.returncode}\n")
        f.write("--- STDOUT ---\n")
        f.write(result.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
        f.write("\n\n")
        
        # Run the MilitaryManager test
        result = run_test("MilitaryManager test", "tests/test_military_simple.py")
        f.write("=== MilitaryManager Test ===\n")
        f.write(f"Return code: {result.returncode}\n")
        f.write("--- STDOUT ---\n")
        f.write(result.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
    
    print(f"Test results saved to {output_file}")

if __name__ == "__main__":
    main()
