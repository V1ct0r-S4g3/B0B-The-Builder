"""Check Python environment and installed packages."""
import sys
import platform
import pkg_resources

def main():
    """Print Python environment information."""
    print("=" * 50)
    print("PYTHON ENVIRONMENT INFORMATION".center(50))
    print("=" * 50)
    
    # Python version
    print(f"\nPython Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Executable: {sys.executable}")
    
    # Installed packages
    print("\nInstalled Packages:")
    print("-" * 50)
    for pkg in sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]):
        print(pkg)
    
    # Check for sc2 package
    try:
        import sc2
        print("\nSC2 Package:")
        print("-" * 50)
        print(f"Version: {getattr(sc2, '__version__', 'unknown')}")
        print(f"Path: {sc2.__file__}")
    except ImportError:
        print("\nSC2 package is not installed.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
