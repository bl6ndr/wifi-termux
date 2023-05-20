import subprocess
import re
from pywifi import PyWiFi, const
from concurrent.futures import ThreadPoolExecutor

def get_wifi_password_method1(ssid):
    try:
        output = subprocess.check_output(["termux-wifi-connectioninfo"])
        output = output.decode("utf-8")

        password = re.search(r'psk=([^\s]+)', output)
        if password:
            return password.group(1)
        else:
            return None

    except subprocess.CalledProcessError:
        return None

def get_wifi_password_method2(ssid):
    try:
        output = subprocess.check_output(["wpa_cli", "-i", "wlan0", "list_networks"])
        output = output.decode("utf-8").split("\n")

        passwords = []
        for line in output[1:]:
            if line:
                network_id = line.split()[0]
                password_output = subprocess.check_output(["wpa_cli", "-i", "wlan0", "get_network", network_id, "psk"])
                password = password_output.decode("utf-8").strip().strip('"')
                passwords.append(password)

        return passwords

    except subprocess.CalledProcessError:
        return None

def get_wifi_password_method3(ssid):
    try:
        wifi = PyWiFi()
        iface = wifi.interfaces()[0]

        iface.scan()
        results = iface.scan_results()

        passwords = []
        for result in results:
            if result.ssid == ssid:
                profile = wifi.add_network_profile()
                profile.ssid = result.ssid
                profile.auth = const.AUTH_ALG_OPEN
                profile.akm.append(const.AKM_TYPE_NONE)

                iface.remove_all_network_profiles()
                temp_profile = iface.add_network_profile(profile)
                iface.connect(temp_profile)

                iface.disconnect()

                if iface.status() == const.IFACE_CONNECTED:
                    password = profile.key
                    passwords.append(password)

        return passwords

    except ImportError:
        return None

def get_wifi_password_method4(ssid):
    try:
        output = subprocess.check_output(["cat", "/data/misc/wifi/wpa_supplicant.conf"])
        output = output.decode("utf-8")

        ssid_passwords = re.findall(r'\n\s*ssid="(.*?)"\n\s*psk="(.*?)"', output)
        passwords = [password for _, password in ssid_passwords if _ == ssid]

        return passwords

    except subprocess.CalledProcessError:
        return None

def get_wifi_password_method5(ssid):
    try:
        output = subprocess.check_output(["termux-wifi-scaninfo"])
        output = output.decode("utf-8")

        ssid_passwords = re.findall(r'\nSSID: (.*?)\nPassphrase: (.*?)\n', output)
        passwords = [password for _, password in ssid_passwords if _ == ssid]

        return passwords

    except subprocess.CalledProcessError:
        return None

def get_wifi_password_method6(ssid):
    try:
        output = subprocess.check_output(["wpa_cli", "-i", "wlan0", "wps_reg", ssid])
        output = output.decode("utf-8").strip()
        password = re.search(r'pin_code=(\d+)', output)
        if password:
            return password.group(1)
        else:
            return None
    except subprocess.CalledProcessError:
        return None

# Prompt user for SSID
ssid = input("Enter the SSID of the network: ")

# Create a thread pool executor with maximum workers equal to the number of methods
with ThreadPoolExecutor(max_workers=6) as executor:
    # Submit the methods to the executor
    futures = [
        executor.submit(method, ssid) for method in [
            get_wifi_password_method1, get_wifi_password_method2, get_wifi_password_method3,
            get_wifi_password_method4, get_wifi_password_method5, get_wifi_password_method6
        ]
    ]

    # Retrieve the results from the completed futures
    results = [future.result() for future in futures]

# Print the passwords
print("Method 1:")
print(results[0])

print("Method 2:")
print(results[1])

print("Method 3:")
print(results[2])

print("Method 4:")
print(results[3])

print("Method 5:")
print(results[4])

print("Method 6:")
print(results[5])
