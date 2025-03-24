import subprocess
import shutil
import sys
import os
import json
from termcolor import colored
import time
from datetime import datetime

# File to store previous user inputs
DATA_FILE = "hydra_config.json"
LOG_FILE = "hydra_log.txt"

def load_previous_inputs():
    """Loads previous inputs from a JSON file if available."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_inputs(data):
    """Saves user inputs to a JSON file for future use."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def log_action(action):
    """Logs actions to a file for debugging and tracking purposes."""
    with open(LOG_FILE, "a") as f:
        f.write(action + "\n")

def show_banner():
    """Displays a banner with a TOXIC FORCE logo."""
    banner = """
    █████╗ ██╗     ██╗
    ██╔══██╗██║     ██║
    ███████║██║     ██║
    ██╔══██║██║     ██║
    ██║  ██║███████╗██╗
    ╚═╝  ╚═╝╚══════╝╚═╝
    """
    for line in banner.split('\n'):
        print(colored(line, 'red'))
        time.sleep(0.2)
    print(colored("\tTOXIC-FORCE Author-> ALI MAHMOUD", 'yellow', attrs=['bold']))
    print(colored(f"\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'green'))  # عرض التاريخ والوقت
    print("\n" + "="*50 + "\n")


def check_hydra():
    """Checks if Hydra is installed, otherwise prompts for installation."""
    if shutil.which("hydra") is None:
        print(colored("[-] Hydra not found.", "red"))
        install_hydra()

def install_hydra():
    """Installs Hydra using the package manager."""
    print(colored("[*] Installing Hydra...", "yellow"))
    try:
        subprocess.run(["sudo", "apt", "install", "-y", "hydra"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(colored("[+] Hydra installed successfully.", "green"))
    except subprocess.CalledProcessError:
        print(colored("[-] Failed to install Hydra. Install manually.", "red"))
        sys.exit(1)

def validate_file(file_path, file_type):
    """Checks if a required file exists before proceeding."""
    if not file_path or not os.path.exists(file_path):
        print(colored(f"[-] {file_type} file not found: {file_path}", "red"))
        sys.exit(1)

def get_input(prompt, key, allow_empty=False):
    """Prompts user for input and saves it for future use."""
    prev_data = load_previous_inputs()
    if key in prev_data:
        default = prev_data[key]
        user_input = input(colored("TOXIC-FORCE > ", "red") + colored(f"{prompt} (Press Enter to keep [{default}]): ", "cyan")).strip()
        if not user_input:
            return default
    else:
        user_input = input(colored("TOXIC-FORCE > ", "red") + colored(prompt, "cyan")).strip()
    if allow_empty and not user_input:
        return None
    prev_data[key] = user_input
    save_inputs(prev_data)
    return user_input

def run_hydra():
    """Runs the Hydra brute force attack based on user input."""
    try:
        check_hydra()
        show_banner()
        protocol = get_input("Select Protocol (SSH/FTP/RDP/HTTP/SMTP):", "protocol")
        target = get_input("Enter target IP/domain:", "target")
        
        username = get_input("Enter a single username (or press Enter to use a file):", "username", allow_empty=True)
        if not username:
            username_file = get_input("Enter username file path:", "username_file")
            validate_file(username_file, "Username")
        else:
            username_file = None

        password = get_input("Enter a single password (or press Enter to use a file):", "password", allow_empty=True)
        if not password:
            password_file = get_input("Enter password file path:", "password_file")
            validate_file(password_file, "Password")
        else:
            password_file = None

        # Use '-l' for single username, '-L' for username file
        user_option = f"-l {username}" if username else f"-L {username_file}"
        pass_option = f"-p {password}" if password else f"-P {password_file}"
        
        # Reduce tasks to 4 if using SSH due to connection limits
        task_limit = "-t 4" if protocol.lower() == "ssh" else ""
        hydra_command = f"hydra {task_limit} {user_option} {pass_option} {target} {protocol.lower()}"
        
        print(colored(f"\n[*] Running Hydra with command:\n{hydra_command}\n", "yellow"))
        log_action(f"Running: {hydra_command}")
        subprocess.run(hydra_command, shell=True)
        
        retry = input(colored("\nDo you want to run again? (y/n): ", "cyan")).strip().lower()
        if retry == "y":
            run_hydra()
        else:
            print(colored("\n[!] Exiting... Goodbye!", "red"))
            sys.exit(0)

    except KeyboardInterrupt:
        print(colored("\n[!] Process interrupted by user. Exiting...", "red"))
        sys.exit(0)



if __name__ == "__main__":
    run_hydra()
