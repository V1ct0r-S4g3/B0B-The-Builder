with open('output_test.txt', 'w') as f:
    f.write("This is a test output\n")
    f.write(f"Python is working!\n")
    try:
        import sc2
        f.write(f"SC2 version: {sc2.__version__ if hasattr(sc2, '__version__') else 'unknown'}\n")
    except ImportError as e:
        f.write(f"SC2 import failed: {e}\n")
