import re


def extract_keywords(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    keywords = ["channel", "sender", "receiver"]
    extracted_lines = []

    for line in lines:
        if any(keyword in line for keyword in keywords):
            extracted_lines.append(line.strip())

    # with open(output_filename, "w") as outfile:
    #     for line in extracted_lines:
    #         outfile.write(line + "\n")

    return extracted_lines

    # print(f"Extracted lines have been written to {output_filename}")


def extract_info(extracted_lines, output_filename):
    with open(extracted_lines, "r") as file:
        lines = file.readlines()

    results = []

    for line in lines:
        # Extract the rows with 'channel' field
        if "channel" in line:
            parts = line.split()
            if len(parts) >= 9:
                channel = parts[1]
                bitrate = parts[6]
                ninth_field = parts[8]
                # results.append(f"channel {channel}\n-b {bitrate}\n{ninth_field}\n")
                results.append(f"channel {channel}\nbitrate {ninth_field}")

        # Extract the rows with 'sender' field
        elif "sender" in line:
            parts = line.split()
            if len(parts) >= 7:
                sender_info = f"{parts[-3]} {parts[-2]} {parts[-1]}"
                results.append(sender_info)

        # Extract the rows with 'receiver' field
        elif "receiver" in line:
            parts = line.split()
            if len(parts) >= 7:
                receiver_info = f"{parts[-3]} {parts[-2]} {parts[-1]}\n"
                results.append(receiver_info)

    with open(output_filename, "w") as outfile:
        for result in results:
            outfile.write(result + "\n")


if __name__ == "__main__":
    input_filename = "test_Result/security_frequency_bandwidth.txt"
    output_filename = "output_Data/security_frequency_bandwidth.txt"

    extract_info(input_filename, output_filename)
    # print(
    #     f"Data extracted from {input_filename} have been written to {output_filename}"
    # )
