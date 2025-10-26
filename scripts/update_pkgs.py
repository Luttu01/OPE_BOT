import subprocess
import sys
import json

def fetch_outdated_packages():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True, 
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception:
        print("Something went wrong fetching outdated packages")
        sys.exit()

def update_pkg(pkg: str):
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", pkg],
            check=True
        )
        return True
    except Exception:
        print(f"Something went wrong updating: {pkg}")
        return False

def main():
    outdated_pkgs = fetch_outdated_packages()
    if not outdated_pkgs:
        print("No outdated packages found.")
        return
    for pkg in outdated_pkgs:
        print(pkg['name'])
        if update_pkg(pkg['name']):
            print(f"successfully updated: {pkg['name']}")

    print("Update complete.")

if __name__ == "__main__":
    main()