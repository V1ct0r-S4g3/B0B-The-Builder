"""Simple test to verify Python output."""
import sys

def main():
    """Print test messages to different output streams."""
    print("This is a test message to stdout")
    print("This is a test message to stderr", file=sys.stderr)
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write("This is a test message to file\n")
    print("Test complete!")

if __name__ == "__main__":
    main()
