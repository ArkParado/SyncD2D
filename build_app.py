#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyncD2D Build Script
Builds standalone executables for Windows, macOS, and Linux
All outputs stored in SyncD2D_App folder
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Fix encoding for Windows CI
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_platform_info():
    """Detect current platform"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows', '.exe', 'app_icon.ico'
    elif system == 'darwin':
        return 'macos', '', 'app_icon.icns'
    else:
        return 'linux', '', 'app_icon.png'

def build_app():
    """Build the application using PyInstaller"""
    
    platform_name, ext, icon_file = get_platform_info()
    
    # Get script directory (SyncD2D_App folder)
    script_dir = Path(__file__).parent.absolute()
    build_dir = script_dir / 'build'
    dist_dir = script_dir / 'dist'
    spec_dir = script_dir
    
    print(f"Building SyncD2D for {platform_name.upper()}...")
    print(f"Working directory: {script_dir}")
    
    # Clean previous builds
    if build_dir.exists():
        print(f"Cleaning old build folder...")
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        print(f"Cleaning old dist folder...")
        shutil.rmtree(dist_dir)
    
    # Remove old spec file
    spec_file = script_dir / f'SyncD2D.spec'
    if spec_file.exists():
        spec_file.unlink()
    
    # Base PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',  # Use current Python
        '--onefile',                          # Single executable
        '--console',                          # Console app (terminal)
        '--name', 'SyncD2D',                 # Output name (no extension)
        '--clean',                           # Clean build
        '--noconfirm',                       # Overwrite without asking
        '--distpath', str(dist_dir),         # Output to SyncD2D_App/dist
        '--workpath', str(build_dir),        # Build in SyncD2D_App/build
        '--specpath', str(spec_dir),         # Spec in SyncD2D_App
    ]
    
    # Add icon if exists
    icon_path = script_dir / icon_file
    if icon_path.exists():
        cmd.extend(['--icon', str(icon_path)])
        print(f"Using icon: {icon_file}")
    
    # Hidden imports for runtime modules
    cmd.extend([
        '--hidden-import', 'tqdm',
        '--hidden-import', 'hashlib',
        '--hidden-import', 'json',
        '--hidden-import', 'logging',
        '--hidden-import', 'threading',
        '--hidden-import', 'concurrent.futures',
        '--hidden-import', 'pathlib',
        '--hidden-import', 'shutil',
        '--hidden-import', 'datetime',
    ])
    
    # Platform-specific imports
    if platform_name == 'windows':
        cmd.extend([
            '--hidden-import', 'msvcrt',
        ])
    else:
        cmd.extend([
            '--hidden-import', 'termios',
            '--hidden-import', 'tty',
        ])
    
    # Add main script (full path)
    main_script = script_dir / 'file_sync.py'
    cmd.append(str(main_script))
    
    print(f"\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    # Run PyInstaller
    try:
        # Change to script directory before building
        original_dir = Path.cwd()
        os.chdir(script_dir)
        
        result = subprocess.run(cmd, check=True, cwd=script_dir)
        
        # Return to original directory
        os.chdir(original_dir)
        
        # Check if executable was created
        executable_name = f'SyncD2D{ext}'
        executable_path = dist_dir / executable_name
        
        if not executable_path.exists():
            # Try without extension for Unix systems
            executable_path = dist_dir / 'SyncD2D'
        
        if executable_path.exists():
            # Make executable on Unix systems
            if platform_name != 'windows':
                os.chmod(executable_path, 0o755)
            
            print("\n" + "="*60)
            print("BUILD SUCCESSFUL!")
            print("="*60)
            print(f"\nExecutable location:")
            print(f"   {executable_path.absolute()}")
            print(f"\nAll build files are in:")
            print(f"   {script_dir}")
            print(f"\nYou can now distribute this file!")
            print(f"   Users can double-click to run (no Python needed)")
            
            # Show file size
            size_mb = executable_path.stat().st_size / (1024 * 1024)
            print(f"\nExecutable size: {size_mb:.2f} MB")
            print("="*60 + "\n")
            
            return True
        else:
            print(f"\nExecutable not found at: {executable_path}")
            print(f"   Check {dist_dir} for output files")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False
    finally:
        # Always return to original directory
        try:
            os.chdir(original_dir)
        except:
            pass

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    script_dir = Path(__file__).parent.absolute()
    requirements_file = script_dir / 'requirements.txt'
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '-r', str(requirements_file),
            '--upgrade'
        ], check=True)
        print("Dependencies installed\n")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        print("   Try manually: pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("    SyncD2D Application Builder v1.0")
    print("    Build standalone executables")
    print("=" * 60)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    
    print(f"Script directory: {script_dir}\n")
    
    # Check if requirements.txt exists
    requirements_file = script_dir / 'requirements.txt'
    if not requirements_file.exists():
        print("ERROR: requirements.txt not found in SyncD2D_App folder!")
        print("   Create it first with the dependencies")
        sys.exit(1)
    
    # Check if main script exists
    main_script = script_dir / 'file_sync.py'
    if not main_script.exists():
        print("ERROR: file_sync.py not found in SyncD2D_App folder!")
        print(f"   Expected location: {main_script}")
        print("   Make sure your script is in the SyncD2D_App folder")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Build the app
    if build_app():
        sys.exit(0)
    else:
        sys.exit(1)