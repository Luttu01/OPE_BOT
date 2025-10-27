import subprocess
import shutil
import sys
from pathlib import Path

def main():
    yt_url = input("Insert youtube link: ").strip()
    
    if not yt_url:
        raise Exception("No YT url given.")
    
    pwd = Path(__file__).resolve().parent
    out_dir = pwd / "tmp"
    out_dir.mkdir(exist_ok=True)

    if shutil.which("yt-dlp"):
        runner = ["yt-dlp"]
    else:
        runner = [sys.executable, "-m", "yt-dlp"]

    cmd = runner + [
        "-x", "--audio-format", "mp3",
        "-o", str(out_dir / "%(title)s.%(ext)s"),
        yt_url
    ]

    try:
        subprocess.run(
            cmd,
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error")

    input("Press any key to exit...")

if __name__ == "__main__":
    main()