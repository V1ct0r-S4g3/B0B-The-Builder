"""Check Python environment and installed packages."""
import sys
import platform
import subprocess
import pkg_resources

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 50)
    print(f"{title}".center(50))
    print("=" * 50)

def check_python_version():
    """Print Python version information."""
    print_section("PYTHON VERSION")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")

def check_installed_packages():
    """List installed Python packages."""
    print_section("INSTALLED PACKAGES")
    try:
        installed_packages = [
            f"{d.key}=={d.version}" for d in pkg_resources.working_set
        ]
        installed_packages.sort()
        print("\n".join(installed_packages))
    except Exception as e:
        print(f"Error getting installed packages: {e}")

def check_sc2_installation():
    """Check SC2 installation."""
    print_section("SC2 INSTALLATION CHECK")
    try:
        import sc2
        print(f"SC2 Python package version: {sc2.__version__}")
        print(f"SC2 package location: {sc2.__file__}")
    except ImportError as e:
        print(f"SC2 package not found: {e}")
    except Exception as e:
        print(f"Error checking SC2 installation: {e}")

def check_environment_variables():
    """Check important environment variables."""
    print_section("ENVIRONMENT VARIABLES")
    vars_to_check = [
        'PYTHONPATH',
        'SC2PATH',
        'PATH'
    ]
    for var in vars_to_check:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")

if __name__ == "__main__":
    import os
    check_python_version()
    check_environment_variables()
    check_sc2_installation()
    check_installed_packages()
