import subprocess
import re
from pywifi import PyWiFi, const

# Method 1: Using termux-wifi-connectioninfo
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
        print("Unable to retrieve WiFi password.")

# Method 2: Using wpa_cli command-line tool
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
        print("Unable to retrieve WiFi passwords.")

# Method 3: Using the pywifi library
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
        print("pywifi library is not installed.")
    except Exception as e:
        print("Unable to retrieve WiFi passwords:", str(e))

# Method 4: Parsing saved WiFi configurations
def get_wifi_password_method4(ssid):
    try:
        output = subprocess.check_output(["cat", "/data/misc/wifi/wpa_supplicant.conf"])
        output = output.decode("utf-8")

        ssid_passwords = re.findall(r'\n\s*ssid="(.*?)"\n\s*psk="(.*?)"', output)
        passwords = [password for _, password in ssid_passwords if _ == ssid]

        return passwords

    except subprocess.CalledProcessError:
        print("Unable to retrieve WiFi passwords.")

# Method 5: Using the termux-wifi-scaninfo and termux-wifi-getpass tools
def get_wifi_password_method5(ssid):
    try:
        output = subprocess.check_output(["termux-wifi-scaninfo"])
        output = output.decode("utf-8")

        ssid_passwords = re.findall(r'\nSSID: (.*?)\nPassphrase: (.*?)\n', output)
        passwords = [password for _, password in ssid_passwords if _ == ssid]

        return passwords

    except subprocess.CalledProcessError:
        print("Unable to retrieve WiFi passwords.")

# Method 6: Using WPA/WPS
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
        print("Unable to retrieve WPA/WPS password.")

# Prompt user for SSID
ssid = input("Enter the SSID of the network: ")

# Calling the methods and printing the passwords
print("Method 1:")
print(get_wifi_password_method1(ssid))

print("Method 2:")
print(get_wifi_password_method2(ssid))

print("Method 3:")
print(get_wifi_password_method3(ssid))

print("Method 4:")
print(get_wifi_password_method4(ssid))

print("Method 5:")
print(get_wifi_password_method5(ssid))

print("Method 6:")
print(get_wifi_password_method6(ssid))
