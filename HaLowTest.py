import paramiko
import time
import sys
import threading


class Host:
    def __init__(self, hostIP, username, password):
        self.hostIP = hostIP
        self.username = username
        self.password = password


def update_channel_AP(host, channel_ID, remote_file_path):

    try:
        # Create SSH client
        client = paramiko.SSHClient()
        # Automatically add SSH key to target host (only used on first connection)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # connect to remote host
        print(f"Connecting to {host.hostIP}...")
        client.connect(
            hostname=host.hostIP, username=host.username, password=host.password
        )
        print(f"Connected to {host.hostIP}")

        # read data from remote host
        sftp = client.open_sftp()
        with sftp.open(remote_file_path, "r") as remote_file:
            lines = remote_file.readlines()

        # modify
        modified_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("channel="):
                # If the line starts with 'channel=', check if there is '#'
                if not stripped_line == f"channel={channel_ID}":
                    line = f"#{line}"
                # If 'channel=channel_id' is found, remove the prefix '#' at the beginning of the line
            if stripped_line == f"#channel={channel_ID}":
                line = line.lstrip("#")
            modified_lines.append(line)

        # Write the modified content back to the file
        with sftp.open(remote_file_path, "w") as file:
            file.writelines(modified_lines)

        print("Channel number updated successfully.")
        # close sftp connetion
        sftp.close()

        client.close()
        # print(f"Connection to {host.hostIP} closed")

    except Exception as e:
        print(f"Failed to modify file on {host.hostIP}: {e}")


def execute_command_on_host(host, command):
    try:

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {host.hostIP}...")
        client.connect(
            hostname=host.hostIP, username=host.username, password=host.password
        )
        print(f"Connected to {host.hostIP}")

        # Execute the command in remote host
        stdin, stdout, stderr = client.exec_command(command)

        # Ensure that the command has been executed completely
        stdout.channel.recv_exit_status()

        # close
        client.close()
        print(f"Connection to {host.hostIP} closed")

    except Exception as e:
        print(f"Failed to execute command on {host.hostIP}: {e}")


def execute_iperf3_AP_command(host, command_AP):
    try:

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {host.hostIP}...")
        client.connect(
            hostname=host.hostIP, username=host.username, password=host.password
        )
        print(f"Connected to {host.hostIP}")

        # Execute and Ensure
        stdin, stdout, stderr = client.exec_command(command_AP)
        stdout.channel.recv_exit_status()

        # close
        client.close()
        print(f"iperf3 server is listening...")

        # event.set()

    except Exception as e:
        print(f"Failed to execute command on {host.hostIP}: {e}")


def execute_iperf3_STA_command(host, command_STA, local_output_file):
    try:

        # event.wait()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {host.hostIP}...")
        client.connect(
            hostname=host.hostIP, username=host.username, password=host.password
        )
        print(f"Connected to {host.hostIP}")

        for command in command_STA:

            stdin, stdout, stderr = client.exec_command(command)

            # Ensure
            stdout.channel.recv_exit_status()

            # Obtain output and error information of the command
            output = stdout.read().decode()
            error = stderr.read().decode()

            # Store output to a local file
            with open(local_output_file, "a") as file:
                file.write(
                    "---------------------------------------------------------------------\n"
                )
                file.write(f"channel {channel_ID} with {command} testing:\n")
                file.write(output)

            # Attach error information to local file (optional)
            with open(local_output_file, "a") as file:
                file.write(error)

        # close
        client.close()
        print(f"Command executed and output saved to {local_output_file}")

    except Exception as e:
        print(f"Failed to execute command on {host.hostIP}: {e}")


def check_connection(host, command_Cli, channel_ID):
    try:

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {host.hostIP}...")
        client.connect(
            hostname=host.hostIP, username=host.username, password=host.password
        )
        print(f"Connected to {host.hostIP}")

        stdin, stdout, stderr = client.exec_command(command_Cli)

        output = stdout.read().decode()
        # error = stderr.read().decode()

        # Check if the 'MAC80211_freq' field contains the specified 'channel_id'
        for line in output.splitlines():
            if "MAC80211_freq" in line:
                if f"({channel_ID})" in line:
                    return 1
        return 0

    except Exception as e:
        print(f"Failed to execute command on {host.hostIP}: {e}")
    finally:
        client.close()
        # print(f"Connection to {host.hostIP} closed")


if __name__ == "__main__":

    # ap_event = threading.Event()

    channel_ID = 162

    # power fixed: 1-30
    # power_level = 15

    # Test: security, frequency, bandwidth
    # local_output_file = "test_Result/security_frequency_bandwidth.txt"

    # 5m_Test: security, frequency, bandwidth
    # local_output_file = "test_Result/5m_security_frequency_bandwidth.txt"

    # # Test: power, frequency, bandwidth, 1:WPA2-PSK
    # local_output_file = "test_Result/power_frequency_bandwidth.txt"

    # # 5m_Test: power, frequency, bandwidth, 1:WPA2-PSK
    # local_output_file = "test_Result/5m_power_frequency_bandwidth.txt"

    # Test: GI short, frequency, bandwidth, 0:OFF, power:limited 24
    # local_output_file = "test_Result/GI_frequency_bandwidth.txt"

    # 5m_Test: GI short, frequency, bandwidth, 0:OFF, power:limited 24
    local_output_file = "test_Result/5m_GI_frequency_bandwidth.txt"

    # Test: GI short, frequency, bandwidth, 0:OFF, power:fixed 1
    # local_output_file = "test_Result/GI_power_frequency_bandwidth.txt"

    remote_file_path = "/home/pi/nrc_pkg/script/conf/AU/ap_halow_open.conf"

    iperf3_server = "192.168.200.1"

    hostAP = Host("192.168.1.101", "pi", "raspberry")
    hostSTA = Host("192.168.1.100", "pi", "raspberry")

    # # security_mode: 0:OFF
    command_AP_Start = "cd nrc_pkg/script/; ./start.py 1 0 AU {}".format(channel_ID)
    command_STA_Start = "cd nrc_pkg/script/; ./start.py 0 0 AU {}".format(channel_ID)

    # security_mode: 1:WPA2-PSK
    # command_AP_Start = "cd nrc_pkg/script/; ./start.py 1 1 AU {}".format(channel_ID)
    # command_STA_Start = "cd nrc_pkg/script/; ./start.py 0 1 AU {}".format(channel_ID)

    command_AP_Stop = "cd nrc_pkg/script/; ./stop.py"
    command_STA_Stop = "cd nrc_pkg/script/; ./stop.py"

    # command_Tx_Power = "cd nrc_pkg/script/; ./cli_app set txpwr fixed {}".format(
    #     power_level
    # )
    command_GI = "cd nrc_pkg/script/; ./cli_app set gi short"

    command_iperf3_AP = "pkill iperf3; iperf3 -s -D"
    command_iperf3_STA = [
        f"iperf3 -c {iperf3_server} -u -b 100k -t 10",
        f"iperf3 -c {iperf3_server} -u -b 1m -t 10",
        f"iperf3 -c {iperf3_server} -u -b 10m -t 10",
    ]
    #   f"iperf3 -c {iperf3_server} -u -b 20m -t 10"]

    command_Cli = "cd nrc_pkg/script/; ./cli_app show config"

    execute_command_on_host(hostAP, command_AP_Stop)
    # time.sleep(3)
    execute_command_on_host(hostSTA, command_STA_Stop)
    # time.sleep(3)
    update_channel_AP(hostAP, channel_ID, remote_file_path)
    execute_command_on_host(hostAP, command_AP_Start)
    # time.sleep(2)
    execute_command_on_host(hostSTA, command_STA_Start)
    # time.sleep(2)
    if check_connection(hostSTA, command_Cli, channel_ID):
        print("AP and STA setup successfully!")
    else:
        print("Hmm...You should have a check!")
        sys.exit(0)
    # # print (f"Now let's test the Tx power with {power_level}")
    # execute_command_on_host(hostSTA, command_Tx_Power)
    # time.sleep(1)
    print(f"Now let's test the GI short with {channel_ID}")
    execute_command_on_host(hostAP, command_GI)
    time.sleep(1)

    execute_iperf3_AP_command(hostAP, command_iperf3_AP)
    # time.sleep(3)

    # ap_thread = threading.Thread(
    #     target=execute_iperf3_AP_command, args=(hostAP, command_iperf3_AP, ap_event)
    # )
    # ap_thread.start()

    # sta_thread = threading.Thread(
    #     target=execute_iperf3_STA_command,
    #     args=(hostSTA, command_iperf3_STA, local_output_file, ap_event),
    # )
    # sta_thread.start()

    # ap_thread.join()
    # sta_thread.join()

    execute_iperf3_STA_command(hostSTA, command_iperf3_STA, local_output_file)
