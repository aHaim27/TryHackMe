#!/usr/bin/env python3
import subprocess
import sys

TOOLS = [
    "hashcat",
    "crunch",
    "aircrack-ng",
    "john",
    "gobuster",
    "ffuf",
    "hydra",
    "dirb",
    "dirbuster",
    "nmap",
    "openvpn",
    "firefox-esr",
    "burpsuite",
    "seclists"
]

def run(cmd):
    try:
        print(f"\n[+] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"[-] Failed: {' '.join(cmd)}")

def update_system():
    print("[+] Updating system packages...")
    run(["sudo", "apt", "update", "-y"])
    run(["sudo", "apt", "upgrade", "-y"])

def install_tools():
    print("[+] Installing tools...")

    for tool in TOOLS:
        run(["sudo", "apt", "install", "-y", tool])

def install_optional_wordlists():
    print("[+] Ensuring SecLists is available...")

    seclists_path = "/usr/share/seclists"
    try:
        import os
        if os.path.exists(seclists_path):
            print("[+] SecLists already installed.")
        else:
            print("[-] SecLists path not found after install, check manually.")
    except Exception as e:
        print(f"[-] Error checking SecLists: {e}")

def main():
    print("""
    =====================================
           Alon's Tools Installer
    =====================================
    """)

    choice = input("Do you want to update system first? (y/n): ").lower()

    if choice == "y":
        update_system()

    install_tools()
    install_optional_wordlists()

    print("\n[+] Done! Your lab environment is ready 🚀")

if __name__ == "__main__":
    if not sys.platform.startswith("linux"):
        print("[-] This script is intended for Linux (Kali/Ubuntu).")
        sys.exit(1)

    main()
