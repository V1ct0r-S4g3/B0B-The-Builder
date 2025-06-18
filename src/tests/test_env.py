with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write("Python environment test\n")
    f.write(f"Python version: {__import__('sys').version}\n")
    f.write(f"Current directory: {__import__('os').getcwd()}\n")
    
    try:
        import sc2
        f.write("SC2 module found!\n")
        f.write(f"SC2 version: {getattr(sc2, '__version__', 'unknown')}\n")
    except ImportError:
        f.write("SC2 module not found\n")
    
    f.write("Test completed successfully!\n")
