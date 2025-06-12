#!/usr/bin/env python3
"""
ANTI-SCAM API Startup Script

This script provides a robust way to start the FastAPI application with
proper environment validation, dependency checks, and error handling.
"""

import os
import sys
import subprocess
import platform
import signal
import time
from pathlib import Path
from typing import Optional, List
import argparse


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """Print colored message to console"""
    print(f"{color}{message}{Colors.END}")


def print_banner():
    """Print startup banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                      ANTI-SCAM API                           ║
║                Comprehensive Fact-Checking Pipeline          ║
║                         Version 2.0.0                        ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)


def check_python_version() -> bool:
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print_colored(f"✓ Python {sys.version.split()[0]} (Compatible)", Colors.GREEN)
        return True
    else:
        print_colored(f"✗ Python {sys.version.split()[0]} (Requires >= {'.'.join(map(str, required_version))})", Colors.RED)
        return False


def check_environment_variables() -> bool:
    """Check if required environment variables are set"""
    print_colored("\n📋 Checking Environment Variables:", Colors.BLUE)
    
    required_vars = ["CLAIMBUSTER_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"]
    optional_vars = ["OPENAI_API_KEY", "HUGGINGFACE_API_KEY"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.getenv(var):
            print_colored(f"  ✓ {var}: Set", Colors.GREEN)
        else:
            print_colored(f"  ✗ {var}: Not set", Colors.RED)
            missing_required.append(var)
    
    for var in optional_vars:
        if os.getenv(var):
            print_colored(f"  ✓ {var}: Set (Optional)", Colors.GREEN)
        else:
            print_colored(f"  ! {var}: Not set (Optional)", Colors.YELLOW)
            missing_optional.append(var)
    
    if missing_required:
        print_colored(f"\n⚠️  Missing required environment variables: {', '.join(missing_required)}", Colors.RED)
        print_colored("   Some API features may not work properly.", Colors.YELLOW)
        return False
    
    return True


def check_dependencies() -> bool:
    """Check if required Python packages are installed"""
    print_colored("\n📦 Checking Dependencies:", Colors.BLUE)
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "python-dotenv",
        "transformers",
        "torch",
        "googletrans",
        "requests",
        "numpy",
        "pandas"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_colored(f"  ✓ {package}", Colors.GREEN)
        except ImportError:
            print_colored(f"  ✗ {package}", Colors.RED)
            missing_packages.append(package)
    
    if missing_packages:
        print_colored(f"\n⚠️  Missing packages: {', '.join(missing_packages)}", Colors.RED)
        print_colored("   Run: pip install -r requirements.txt", Colors.YELLOW)
        return False
    
    return True


def check_file_structure() -> bool:
    """Check if required files and directories exist"""
    print_colored("\n📁 Checking File Structure:", Colors.BLUE)
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env",
        "models/",
        "converters/",
        "translator/",
        "web_searcher/"
    ]
    
    missing_files = []
    current_dir = Path.cwd()
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print_colored(f"  ✓ {file_path}", Colors.GREEN)
        else:
            print_colored(f"  ✗ {file_path}", Colors.RED)
            missing_files.append(file_path)
    
    if missing_files:
        print_colored(f"\n⚠️  Missing files/directories: {', '.join(missing_files)}", Colors.RED)
        return False
    
    return True


def check_port_availability(port: int) -> bool:
    """Check if the specified port is available"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print_colored(f"✓ Port {port} is available", Colors.GREEN)
            return True
    except OSError:
        print_colored(f"✗ Port {port} is already in use", Colors.RED)
        return False


def install_dependencies() -> bool:
    """Install missing dependencies"""
    print_colored("\n📦 Installing dependencies...", Colors.YELLOW)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print_colored("✓ Dependencies installed successfully", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Failed to install dependencies: {e}", Colors.RED)
        print_colored(f"Error output: {e.stderr}", Colors.RED)
        return False


def create_env_file() -> None:
    """Create a template .env file if it doesn't exist"""
    env_path = Path(".env")
    
    if not env_path.exists():
        env_template = """# ANTI-SCAM API Environment Variables
# Copy this file and fill in your actual API keys

# Required API Keys
CLAIMBUSTER_API_KEY=your_claimbuster_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Optional API Keys
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
"""
        env_path.write_text(env_template)
        print_colored("✓ Created .env template file", Colors.GREEN)
        print_colored("  Please fill in your API keys in the .env file", Colors.YELLOW)


def start_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = True, 
              log_level: str = "info", workers: int = 1) -> None:
    """Start the FastAPI application using uvicorn"""
    
    print_colored(f"\n🚀 Starting ANTI-SCAM API...", Colors.GREEN)
    print_colored(f"   Host: {host}", Colors.CYAN)
    print_colored(f"   Port: {port}", Colors.CYAN)
    print_colored(f"   Reload: {reload}", Colors.CYAN)
    print_colored(f"   Log Level: {log_level}", Colors.CYAN)
    print_colored(f"   Workers: {workers}", Colors.CYAN)
    
    cmd = [
        "uvicorn",
        "main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", log_level
    ]
    
    if reload:
        cmd.append("--reload")
    
    if workers > 1 and not reload:
        cmd.extend(["--workers", str(workers)])
    
    try:
        print_colored(f"\n🌐 API will be available at: http://{host}:{port}", Colors.BOLD + Colors.GREEN)
        print_colored(f"📚 API Documentation: http://{host}:{port}/docs", Colors.BOLD + Colors.BLUE)
        print_colored(f"🔄 Alternative Docs: http://{host}:{port}/redoc", Colors.BOLD + Colors.BLUE)
        print_colored(f"\n💡 Press Ctrl+C to stop the server\n", Colors.YELLOW)
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Failed to start API: {e}", Colors.RED)
        sys.exit(1)
    except KeyboardInterrupt:
        print_colored(f"\n\n🛑 API server stopped by user", Colors.YELLOW)
        sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Start the ANTI-SCAM API with comprehensive checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_api.py                    # Start with default settings
  python start_api.py --port 8080        # Start on port 8080
  python start_api.py --no-reload        # Start without auto-reload
  python start_api.py --production        # Start in production mode
  python start_api.py --skip-checks      # Skip all validation checks
        """
    )
    
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--log-level", default="info", choices=["critical", "error", "warning", "info", "debug"], help="Log level")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--production", action="store_true", help="Start in production mode")
    parser.add_argument("--skip-checks", action="store_true", help="Skip all validation checks")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies before starting")
    parser.add_argument("--create-env", action="store_true", help="Create .env template file")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Handle special flags
    if args.create_env:
        create_env_file()
        return
    
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
        return
    
    # Production mode settings
    if args.production:
        args.no_reload = True
        args.log_level = "warning"
        if args.workers == 1:
            args.workers = 2
        print_colored("🏭 Production mode enabled", Colors.MAGENTA)
    
    # Run validation checks
    if not args.skip_checks:
        print_colored("🔍 Running validation checks...", Colors.BLUE)
        
        checks_passed = True
        
        # Check Python version
        if not check_python_version():
            checks_passed = False
        
        # Check file structure
        if not check_file_structure():
            checks_passed = False
        
        # Check dependencies
        if not check_dependencies():
            checks_passed = False
            print_colored("\n💡 Tip: Use --install-deps to install missing dependencies", Colors.YELLOW)
        
        # Check environment variables
        if not check_environment_variables():
            print_colored("\n💡 Tip: Use --create-env to create a template .env file", Colors.YELLOW)
        
        # Check port availability
        if not check_port_availability(args.port):
            checks_passed = False
        
        if not checks_passed:
            print_colored(f"\n❌ Some validation checks failed.", Colors.RED)
            print_colored("   You can use --skip-checks to bypass validation.", Colors.YELLOW)
            
            response = input(f"\n{Colors.YELLOW}Continue anyway? (y/N): {Colors.END}")
            if response.lower() not in ['y', 'yes']:
                sys.exit(1)
        else:
            print_colored(f"\n✅ All validation checks passed!", Colors.GREEN)
    
    # Start the API
    start_api(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level,
        workers=args.workers
    )


if __name__ == "__main__":
    main()
