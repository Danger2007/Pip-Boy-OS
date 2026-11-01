import os
import zipfile
import io
import requests
import pip_boy_os

def main():
    print("Downloading assets from GitHub Repo please wait...")
    url = "https://github.com/Danger2007/Pip-Boy-OS/archive/refs/heads/main.zip"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Find the installation directory of the site-packages package
        pkg_dir = os.path.dirname(pip_boy_os.__file__)
        
        print("Extracting assets...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # The GitHub zip creates a main folder (e.g., Pip-Boy-OS-main)
            # Extract and move the necessary folders (fonts, images, sounds, objs)
            for filename in z.namelist():
                if any(folder in filename for folder in ['fonts/', 'images/', 'sounds/', 'objs/']):
                    z.extract(filename, pkg_dir)
                    
        print("Assets configured successfully! You can now launch pipboy-os.")
    except Exception as e:
        print(f"Error occurred while downloading assets: {e}")

if __name__ == "__main__":
    main()