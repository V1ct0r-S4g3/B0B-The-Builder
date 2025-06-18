"""Test file writing and output capture."""

def main():
    """Test file writing and print output."""
    print("Starting test...")
    
    # Try writing to a file
    try:
        with open("test_output_direct.txt", "w") as f:
            f.write("Direct file write test\n")
            f.write("This is a test message.\n")
            f.write("Testing 1, 2, 3...\n")
        print("Successfully wrote to test_output_direct.txt")
    except Exception as e:
        print(f"Error writing to file: {e}")
    
    # Try running a command
    import subprocess
    try:
        result = subprocess.run(
            ["python", "-c", "print('Hello from subprocess')"],
            capture_output=True,
            text=True
        )
        with open("test_subprocess_output.txt", "w") as f:
            f.write(f"Return code: {result.returncode}\n")
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("=== STDERR ===\n")
            f.write(result.stderr)
        print("Successfully captured subprocess output")
    except Exception as e:
        print(f"Error running subprocess: {e}")

if __name__ == "__main__":
    main()
