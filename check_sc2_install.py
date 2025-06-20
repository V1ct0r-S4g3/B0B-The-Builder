"""
Diagnostic script to check StarCraft II installation and system compatibility.
"""
import os
import sys
import platform
import subprocess
import ctypes
import winreg
from pathlib import Path

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_os_requirements():
    """Check if the system meets the minimum OS requirements."""
    print("\n=== Operating System ===")
    print(f"System: {platform.system()} {platform.release()} {platform.version()}")
    print(f"Processor: {platform.processor()}")
    print(f"Architecture: {'64-bit' if sys.maxsize > 2**32 else '32-bit'}")
    print(f"Running as admin: {is_admin()}")

def check_directx():
    """Check DirectX version."""
    try:
        print("\n=== DirectX Version ===")
        import wmi
        c = wmi.WMI()
        for os in c.Win32_OperatingSystem():
            print(f"OS: {os.Caption}")
        for dx in c.Win32_VideoController():
            print(f"Graphics: {dx.Name} (Driver: {dx.DriverVersion if hasattr(dx, 'DriverVersion') else 'N/A'})")
    except ImportError:
        print("Install 'wmi' package for detailed DirectX info: pip install wmi")

def check_sc2_install():
    """Check StarCraft II installation."""
    print("\n=== StarCraft II Installation ===")
    sc2_paths = [
        Path(r"D:\Battle.net\StarCraft2"),
        Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'StarCraft II',
        Path(os.environ.get('PROGRAMFILES', '')) / 'StarCraft II',
    ]
    
    found = False
    for path in sc2_paths:
        if path.exists():
            found = True
            print(f"Found SC2 at: {path}")
            
            # Check important files
            exe_path = path / 'Versions' / 'Base94137' / 'SC2_x64.exe'
            print(f"  - SC2_x64.exe: {'Found' if exe_path.exists() else 'Missing'}")
            
            # Get version info if available
            if exe_path.exists():
                try:
                    info = subprocess.check_output(
                        ['wmic', 'datafile', 'where', f'name=\"{exe_path}\"', 'get', 'Version,LastModified', '/format:list'],
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    print(info.strip())
                except:
                    pass
    
    if not found:
        print("StarCraft II installation not found in standard locations.")

def check_system_requirements():
    """Check system requirements."""
    print("\n=== System Requirements ===")
    # Minimum requirements for SC2
    min_requirements = {
        'OS': 'Windows 10 64-bit',
        'CPU': 'Intel Core i3 or AMD FX 4100',
        'RAM': '4GB',
        'GPU': 'NVIDIA GeForce GTX 650 or AMD Radeon HD 7790',
        'VRAM': '2GB',
        'Storage': '30GB',
        'DirectX': '11'
    }
    
    for req, value in min_requirements.items():
        print(f"{req}: {value}")

def check_dependencies():
    """Check for required system dependencies."""
    print("\n=== Dependencies ===")
    deps = {
        'Visual C++ Redistributable 2015-2022': {
            'x64': '{36f68a90-239c-34df-b58c-64ef301cd628}'
        },
        '.NET Framework': {
            '4.8': 'NDP48'
        }
    }
    
    try:
        # Check VC++ Redist
        print("Visual C++ Redistributable:")
        for name, guid in deps['Visual C++ Redistributable 2015-2022'].items():
            try:
                key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{{{guid}}}"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                version = winreg.QueryValueEx(key, 'DisplayVersion')[0]
                print(f"  - {name}: Installed (v{version})")
            except WindowsError:
                print(f"  - {name}: Not found")
    except Exception as e:
        print(f"  - Error checking VC++ Redist: {e}")
    
    # Check .NET Framework
    try:
        print("\n.NET Framework:")
        for version, release in deps['.NET Framework'].items():
            try:
                key_path = fr"SOFTWARE\Microsoft\NET Framework Setup\NDP\{release}"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                installed = winreg.QueryValueEx(key, 'Version')[0]
                print(f"  - .NET {version}: Installed (v{installed})")
            except WindowsError:
                print(f"  - .NET {version}: Not found")
    except Exception as e:
        print(f"  - Error checking .NET Framework: {e}")

def main():
    print("StarCraft II Installation Diagnostic Tool")
    print("=" * 40)
    
    check_os_requirements()
    check_sc2_install()
    check_system_requirements()
    check_dependencies()
    check_directx()
    
    print("\nRecommendations:")
    print("1. Run the Battle.net launcher and verify StarCraft II game files")
    print("2. Update your graphics drivers")
    print("3. Install the latest Windows updates")
    print("4. Run the game directly from Battle.net launcher first")
    print("5. Check Windows Event Viewer for application crash logs")

if __name__ == "__main__":
    main()
