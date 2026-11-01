import os
import zipfile
import io
import requests
import pip_boy_os
import importlib.util
import shutil
import tempfile

def main():
    print("Downloading assets from GitHub...")
    url = "https://github.com/Danger2007/Pip-Boy-OS/archive/refs/heads/main.zip"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        if hasattr(pip_boy_os, '__file__') and pip_boy_os.__file__:
            pkg_dir = os.path.dirname(os.path.abspath(pip_boy_os.__file__))
        else:
            spec = importlib.util.find_spec("pip_boy_os")
            pkg_dir = os.path.dirname(spec.origin) if spec and spec.origin else os.getcwd()
            
        print("Extraction and configuration of assets in progress...")
        # Create a temporary directory to extract the zip file (to fix a windows limitation)
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(temp_dir)
            
            top_folder = z.namelist()[0].split('/')[0]
            source_pipboy = os.path.join(temp_dir, top_folder, "pip_boy_os")
            
            for folder_name in ['fonts', 'images', 'sounds', 'objs']:
                src_folder = os.path.join(source_pipboy, folder_name)
                dst_folder = os.path.join(pkg_dir, folder_name)
                
                if os.path.exists(src_folder):
                    if os.path.exists(dst_folder):
                        shutil.rmtree(dst_folder)
                    shutil.copytree(src_folder, dst_folder)
                    
        print("Assets configured successfully! You can now start pipboy-os.")
    except Exception as e:
        print(f"Error during asset download: {e}")

if __name__ == "__main__":
    main()