import os
import subprocess
import sys
import re
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog


# --------------------------------------------------------------------------------------------------
def y_n_choice():
    root = tk.Tk()
    root.withdraw()

    while True:
        try:
            user_input = simpledialog.askstring("User Input", "Enter 'yes' to continue or 'no' to skip:", parent=root).lower()
            if user_input not in ['yes', 'y', '', 'no', 'n']:
                raise ValueError("Invalid input, please enter 'yes' or 'no'.")

            return user_input
        except ValueError as ve:
            print("Error:", ve)


def log_setup():
    log_file_path = "script_log.txt"
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write(f"-----------------------------------------------------------------------\n")
            log_file.write(f"                           Host Firewall Compliance                         \n")
            log_file.write(f"-----------------------------------------------------------------------\n")

            log_file.write(f"{current_datetime} - ============ SCRIPT INITIATION ============\n")
    else:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"\n{current_datetime} - ============ PROGRAM EXECUTION ============\n")


def log_changes(changes):
    log_file_path = "script_log.txt"
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a") as log_file:
            log_file.write(f"\nChanges made: {changes}")


def is_ufw_installed():
    return bool(os.system("command -v ufw >/dev/null 2>&1") == 0)

def ensure_ufw_installed():
    root = tk.Tk()
    root.withdraw()

    print("""
\033[91m=============== Installing Host Firewall ===============\033[0m

A firewall utility is required to configure the Linux kernel's netfilter framework via the
iptables or nftables back-end. The Linux kernel's netfilter framework host-based firewall can
protect against threats originating from within a corporate network, including malicious
mobile code and poorly configured software on a host.

Note: Only one firewall utility should be installed and configured. UFW is dependent on
the iptables package.
""")

    if not is_ufw_installed():
        var = simpledialog.askstring("Install UFW", "This point onwards, the configurations require the installation of UFW. Do you want to install the Host firewall? (yes/no):", parent=root).lower()
        var.lower()

        if var == 'y' or var == 'yes' or var == '':
            os.system("apt install ufw")
            line = "Installed UFW"
            log_changes(line)
            print("\n", line)
        elif var == 'n' or var == 'no':
            line = "UFW not installed"
            log_changes(line)
            print("\n", line)
            exit()
    else:
        line = "UFW already installed"
        log_changes(line)
        print("\n", line)

def is_iptables_persistent_installed():
    return bool(os.system("dpkg -s iptables-persistent >/dev/null 2>&1") == 0)


def ensure_iptables_persistent_packages_removed():
    root = tk.Tk()
    root.withdraw()

    print("""
\033[91m============== Removing IP-Persistent Tables ==============\033[0m

Running both `ufw` and the services included in the `iptables-persistent` package may lead
to conflicts.
""")
    if is_iptables_persistent_installed():
        var = simpledialog.askstring("Remove iptables-persistent", "Do you want to remove the iptables-persistent packages? (yes/no):", parent=root).lower()
        var.lower()

        if var == 'y' or var == 'yes' or var == '':
            os.system("apt purge iptables-persistent")
            line = "Iptables persistent packages removed"
            log_changes(line)
            print("\n", line)
        elif var == 'n' or var == 'no':
            line = "Iptables persistent packages skipped by user"
            log_changes(line)
            print("\n", line)
    else:
        line = "Iptables persistent packages already uninstalled"
        log_changes(line)
        print("\n", line)



def is_ufw_enabled():
    try:
        # Run the command to check UFW status
        result = subprocess.run(['ufw', 'status'], capture_output=True, text=True, check=True)

        # Check if the output contains 'Status: active'
        return 'Status: active' in result.stdout
    except FileNotFoundError:
        # Handle the FileNotFoundError
        messagebox.showerror("Error", "'ufw' executable not found. Please ensure that UFW is installed.")
        return False
    except subprocess.CalledProcessError as e:
        # If an error occurs while running the command
        messagebox.showerror("Error", f"Error: {e}")
        return False

def enable_firewall_sequence():

    print("""
\033[91m================== Enabling UFW ==================\033[0m

When running `ufw enable` or starting `ufw` via its initscript, `ufw` will flush its chains.
This is required so `ufw` can maintain a consistent state, but it may drop existing
connections (e.g., SSH). `ufw` does support adding rules before enabling the firewall.
The rules will still be flushed, but the SSH port will be open after enabling the
firewall.

Please note that once `ufw` is 'enabled', it will not flush the chains when
adding or removing rules (but will when modifying a rule or changing the default policy).

By default, `ufw` will prompt when enabling the firewall while running under SSH.
""")
    if not is_ufw_enabled():
        print("\nUFW is not enabled, do you want to enable it, ")
        var=y_n_choice()
        var.lower()
        if var == 'y' or var == 'yes' or var == '':
            print("\nufw will flush its chains.This is good in maintaining a consistent state, but it may drop existing connections (eg ssh)")
            os.system("ufw allow proto tcp from any to any port 22")
            # Run the following command to verify that the ufw daemon is enabled:
            print(" \nverifying that the ufw daemon is enabled:")
            os.system("systemctl is-enabled ufw.service")
            # following command to verify that the ufw daemon is active:
            print(" \nverifying that the ufw daemon is active:")
            os.system("systemctl is-active ufw")
            # Run the following command to verify ufw is active
            print(" \nverifying ufw is active:")
            os.system("ufw status")
            # following command to unmask the ufw daemon
            print("\nunmasking ufw daemon:")
            os.system("systemctl unmask ufw.service")
            # following command to enable and start the ufw daemon:
            print("\nenabling and starting the ufw daemon:")
            os.system("systemctl --now enable ufw.service")
            #following command to enable ufw:
            print("\nEnabling the firewall...")
            os.system("ufw enable")
            line="""
            Commands issued before enabling the firewall:
                ufw allow proto tcp from any to any port 22
                systemctl is-enabled ufw.service
                systemctl is-active ufw
                systemctl unmask ufw.service
                systemctl --now enable ufw.service
            ufw enable
            """
            log_changes(line)
            print("\n",line)
        elif var == 'n' or var == 'no':
            line="User didn't enable the UFW service"
            log_changes(line)
            print("\nExiting UFW enabling mode... continuing to next configurations")
    else:
        line="UFW is already enabled"
        log_changes(line)
        print("\n",line)




def ensure_loopback_configured():
    print("""
    \033[91m================ Configuring the Loopback Interface =================\033[0m

Loopback traffic is generated between processes on the machine and is typically critical to
the operation of the system. The loopback interface is the only place that loopback network
(127.0.0.0/8 for IPv4 and ::1/128 for IPv6) traffic should be seen. All other interfaces
should ignore traffic on this network as an anti-spoofing measure.
""")
    print("\ndo you want to proceed, ")
    var=y_n_choice()
    var.lower()
    if var == 'y' or var == 'yes' or var == '':
        line="""
        User enabled configuring lo interfaces,
        Commands executed when configuring loopback interfaces:
            ufw allow in on lo
            ufw allow out on lo
            ufw deny in from 127.0.0.0/8
            ufw deny in from ::1
            
        """
        log_changes(line)
        print("\nEnabling configurations on lo interfaces...")
        os.system("ufw allow in on lo")
        os.system("ufw allow out on lo")
        os.system("ufw deny in from 127.0.0.0/8")
        os.system("ufw deny in from ::1")
    elif var == 'n' or var == 'no':
        line="Loopback interface not configured"
        log_changes(line)
        print("\n",line)


def ensure_ufw_outbound_connections():
    print("""
\033[91m========= Configuring UFW Outbound Connections =========\033[0m

If rules are not in place for new outbound connections, all packets will be dropped by the
default policy, preventing network usage.
""")
    print("\n Do you want to configure your ufw outbound connections if this set of rules are not in place for new outbound connections all"
                "packets will be dropped by the"
                "default policy preventing network usage.,")
    var=y_n_choice()
    var.lower()
    if var == 'y' or var == 'yes' or var == '':
        # var = input("\n PLease verify all the rules whether it matches all the site policies")
        print("\n implementing a policy to allow all outbound connections on all interfaces:")
        line="""
        User enabled configuring UFW outbound connections,
        below Commands executed when configuring outbound interfaces:
            ufw allow out on all
        """
        log_changes(line)
        print("\nConfiguration successfull ...")
        os.system("ufw allow out on all")

    elif var == 'n' or var == 'no':
        line="User skipped the ufw outbound configurations"
        log_changes(line)
        print("\n Hardening measure skipped")


def get_allow_deny():
    while True:
        try:
            allw_dny = simpledialog.askstring("Enter rule (allow or deny): ").lower()
            if allw_dny not in ['allow', 'deny']:
                raise ValueError("Invalid rule. Please enter either 'allow' or 'deny'.")

            return allw_dny
        except ValueError as ve:
            print("Error:",ve)


def is_valid_decimal(value):
    return 0 <= int(value) <= 255

def is_valid_network_address(address_parts):
    return all(is_valid_decimal(part) for part in address_parts)

def get_network_address():
    while True:
        try:
            netadd = simpledialog.askstring("Enter network address (in the format xxx.xxx.xxx.xxx): ")
            address_parts = netadd.split('.')

            # Use a regular expression to check if the input matches the expected format
            if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', netadd) or not is_valid_network_address(address_parts):
                raise ValueError("Invalid network address format or out-of-range values. Please use xxx.xxx.xxx.xxx format.")

            return netadd
        except ValueError as ve:
             print("\nError:", ve)

def get_proto():
    while True:
        try:
            proto = simpledialog.askstring("Enter protocol (tcp or udp): ").lower()
            if proto not in ['tcp', 'udp']:
                raise ValueError("Invalid protocol. Please enter either 'tcp' or 'udp'.")

            return proto
        except ValueError as ve:
            print("Error:",ve)

def get_mask():
    while True:
        try:
            mask = int(simpledialog.askstring("Enter the whole number value of the subnet mask (16-32): "))
            if 16 <= mask <= 32:
                return str(mask)
            else:
                raise ValueError("\nInvalid subnet mask. Please enter a value between 16 and 32.")
        except ValueError as ve:
            print("\nError:",ve)

def get_ports_as_a_list(script_path):
    result = subprocess.run(['bash', script_path], capture_output=True, text=True)
    ports_list = 0
    if result.returncode == 0:
        # If the script ran successfully, print the output
        # getting numbers from string
        temp = re.findall(r'\d+', result.stdout)
        ports_list = list(map(int, temp))
        print("Open ports with no FW rule")
        for i in range(0, len(ports_list)):
            print(i, ':', ports_list[i])
        return ports_list

    else:
        # If there was an error, print the error message
        print("Error:")
        print(result.stderr)


def get_port_number(script_path):
    while True:
        try:
            ports_list=get_ports_as_a_list(script_path)
            p_no = int(input("Enter the index number of the port to be configured: "))
            if 0 <= p_no <= len(ports_list)-1:
                port_number = ports_list[p_no]
                return str(port_number)
            else:
                raise ValueError("\nInvalid Index Number. Please enter a value between 0 and",len(ports_list))
        except ValueError as ve:
            print("\nError:",ve)
# def ensure_rules_on_ports_banner():
#

def ensure_rules_on_ports(script_path):
    print("""
\033[91m=== Configuring Firewall Rules for All Open Ports ===\033[0m

To reduce the attack surface of a system, all services and ports should be blocked unless required.

Your configuration will follow this format:
    ufw allow from 192.168.1.0/24 to any proto tcp port 443

""")
    print("Do you want to continue configuring firewall rules for a port [Y/n]: ")
    var=y_n_choice()
    if var == 'y' or var == 'yes' or var == '':
        port_number=get_port_number(script_path)
        allow = get_allow_deny()
        netad = get_network_address()
        mask = get_mask()
        proto = get_proto()
        rule = ("ufw " + allow + " from " + netad + "/" + mask + " to any proto " + proto + " port " + str(port_number))
        line=("User configured the follwing port rule\n: "+str(rule))
        log_changes(line)
        os.system(rule)
        input("\nHit enter to continue [enter]: ")
        ensure_rules_on_ports(script_path)
    elif var == 'n' or var == 'no':
        line=("User did not configure firewall rules on ports")
        log_changes(line)
        print("Skipping firewall rule configuration on ports...")

def is_default_deny_policy():
    #check if the deny policies are already configured

    return bool(os.system("ufw status verbose | grep 'Default: deny (incoming), deny (outgoing), deny (routed)' >/dev/null 2>&1") == 0)


def ensure_port_deny_policy():

    print("""
\033[91m================ Default Port Deny Policy ================\033[0m

Any port and protocol not explicitly allowed will be blocked.

Do you want to configure the default deny policy? [Y/n]: """)
    is_default_deny_policy()
    var=y_n_choice()
    var.lower()
    if var == 'y' or var == 'yes' or var == '':
        print("remediation process...")
        print("\n allowing Git...")
        os.system("ufw allow git")
        print("\nallowing http in...")
        os.system("ufw allow in http")
        print("\nallowing http out...")
        os.system("ufw allow out http")
        print("\nallowing https in...")
        os.system("ufw allow in https")
        print("\nallowing https out...")
        os.system("ufw allow out https")
        print("\nallowing port 53 out...")
        os.system("ufw allow out 53")
        print("\nallowing ufw logging on...")
        os.system("ufw logging on")
        print("\ndenying incoming by default...")
        os.system("ufw default deny incoming")
        print("\ndenying outgoing by default...")
        os.system("ufw default deny outgoing")
        print("\ndenying default routing...")
        os.system("ufw default deny routed")
        line="""
        User configured the following default deny policies:
            ufw allow git
            ufw allow in http
            ufw allow out http
            ufw allow in https
            ufw allow out https
            ufw allow out 53
            ufw logging on
            ufw default deny incoming
            ufw default deny outgoing
            ufw default deny routed
        """
        log_changes(line)
    elif var == 'n' or var == 'no':
        line="User skipped configuring default deny policy"
        log_changes(line)
        print("\nexiting port deny policy...")

def scan_system_configuration():
    messagebox.showinfo("Scan", "Scanning the system... shown on terminal")
    print("\n\033[91m==================== Scanning System Configuration ====================\033[0m")
    # Check if UFW is installed
    if is_ufw_installed():
        print("UFW is installed.")
    else:
        print("\033[91mUFW is not installed.\033[0m")

    # Check if iptables-persistent packages are removed
    if  is_iptables_persistent_installed():
        print("\033[91mIptables-persistent packages are not removed.\033[0m")

    # Check if UFW is enabled
    if is_ufw_enabled():
        print("UFW is enabled.")
    else:
        print("\033[91mUFW is not enabled.\033[0m")

    # Check if loopback interface is configured
    try:
        subprocess.run(['ufw', 'status', 'verbose', '|', 'grep', 'in', 'on', 'lo'], check=True, capture_output=True, text=True)
        print("Loopback interface is configured.")
    except subprocess.CalledProcessError:
        print("\033[91mLoopback interface is not configured.\033[0m")

    # Add more checks for other configurations as needed

    print("\nScanning complete.")

# Example usage:



def all_ufw_hardening_controls():
    messagebox.showinfo("Configure", "Configuring the system... (Replace with actual configuration logic)")
    ensure_ufw_installed()
    time.sleep(2)
    ensure_iptables_persistent_packages_removed()
    time.sleep(2)
    enable_firewall_sequence()
    time.sleep(2)
    # ensure_rules_on_ports_banner()
    script_path = 'ufwropnprts.sh'
    ensure_rules_on_ports(script_path)
    time.sleep(2)
    ensure_port_deny_policy()
    time.sleep(2)



#function to askc the user if he wants to do a scan or go straight into configurations and call the relevent function in the script and exit if needed
def scan_or_config():
    print("\n\033[91m==================== UFW CIS Compliance Suite ====================\033[0m")
    print("\nDo you want to scan the system ")
    var=y_n_choice()
    var.lower()
    if var == 'y' or var == 'yes' or var == '':
        scan_system_configuration()
        print("\nExiting...")
        time.sleep(2)
        #ask the user if he needs to do the configurations
        print("\nDo you want to continue to configurations")
        var=y_n_choice()
        var.lower()
        if var == 'y' or var == 'yes' or var == '':
            all_ufw_hardening_controls()
            print("\n\033[91mPress enter to exit the code [enter] \033[0m")
            input()
            print("\nExiting...")
            time.sleep(2)
        if var == 'n' or var == 'no':
            print("\nExiting...")
            time.sleep(2)
    elif var == 'n' or var == 'no':
        print("\nContinuing to configurations...")
        time.sleep(2)
        return

#==========================================================






def main():
    root = tk.Tk()
    root.title("UFW CIS Compliance Suite")

    label = tk.Label(root, text="Do you want to scan or configure the system?")
    label.pack(pady=10)

    scan_button = tk.Button(root, text="Scan", command=scan_system_configuration)
    scan_button.pack(pady=5)

    configure_button = tk.Button(root, text="Configure", command=all_ufw_hardening_controls)
    configure_button.pack(pady=5)

    root.mainloop()








#========================================================== M A I N ======================================
# def main():
# #     #customization-------------------------
# #     text=''
# #     def slow_print(text,**kwargs):
# #         delay=0.05
# #     for char in text:
# #         print(char, end='', flush=True, **kwargs)
# #         time.sleep(delay)
# #
# # # Override the built-in print function
# #     def print(*args, **kwargs):
# #         slow_print(*args, **kwargs)
# #     built_in_print = print
#
#
#
#     try:
#         log_setup()
#         scan_or_config()
#     except FileNotFoundError:
#         # Handle the FileNotFoundError
#         print("Error: 'ufw' executable not found. Please ensure that UFW is installed.")
#     except KeyboardInterrupt:
#         print("\n\nApplication stopped...")



if __name__ == "__main__":
    main()