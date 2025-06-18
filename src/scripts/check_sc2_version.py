import sys
import os

def main():
    print("Python Version:", sys.version)
    print("Python Path:", sys.executable)
    
    try:
        import sc2
        print("\nSC2 Package:")
        print("-" * 40)
        print(f"Version: {getattr(sc2, '__version__', 'unknown')}")
        print(f"Path: {os.path.dirname(sc2.__file__)}")
        
        # Check SC2 installation
        print("\nSC2 Installation:")
        print("-" * 40)
        sc2_path = r"D:\Battle.net\StarCraft2"
        if os.path.exists(sc2_path):
            print(f"✅ Found SC2 at: {sc2_path}")
            
            # Check for SC2 executable
            for root, dirs, files in os.walk(sc2_path):
                if "SC2_x64.exe" in files:
                    exe_path = os.path.join(root, "SC2_x64.exe")
                    print(f"✅ Found SC2 executable: {exe_path}")
                    break
            else:
                print("❌ Could not find SC2_x64.exe in the SC2 directory")
        else:
            print(f"❌ SC2 not found at: {sc2_path}")
            
    except ImportError as e:
        print("\n❌ Error importing sc2:", e)
        print("Install it with: pip install sc2")
    except Exception as e:
        print("\n❌ Unexpected error:", str(e))

if __name__ == "__main__":
    main()
