import os
import csv
import json

wallets_file = 'wallets.txt'
root_dir = 'RFP Allocations'
output_json_1 = 'result_1.json'
output_json_2 = 'result_2.json'
output_json_3 = 'result_3.json'

def read_wallets(file_path):
    with open(file_path, 'r') as f:
        return {line.strip().lower() for line in f}

def parse_allocation(value):
    try:
        value = value.replace(',', '').replace('%', '').strip()
        return float(value)
    except ValueError:
        # print(f"Cannot convert value: {value}")
        return None

def get_allocation_value(row):
    numeric_values = [parse_allocation(value) for value in row if parse_allocation(value) is not None]
    for value in numeric_values:
        if value < 1:
            return value
    return numeric_values[0] if numeric_values else 0.0

def process_csv_file(csv_path, wallet_addresses):
    wallet_allocations = {}
    total_allocation = 0.0

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            if not any(row):
                continue
            try:
                address = row[0].strip().lower()
                if address in wallet_addresses:
                    allocation_value = get_allocation_value(row[1:])
                    if address in wallet_allocations:
                        wallet_allocations[address] += allocation_value
                    else:
                        wallet_allocations[address] = allocation_value
                    total_allocation += allocation_value
            except (IndexError, ValueError) as e:
                print(f"Error processing row: {row}, error: {e}")
                continue

    wallet_allocations = {addr: f"{alloc:.12f}%" for addr, alloc in wallet_allocations.items()}
    return wallet_allocations, total_allocation

def process_all_files(root_dir, wallet_addresses):
    result_dict = {}
    total_allocation_dict = {}

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_path = os.path.join(subdir, file)
                folder_name = os.path.basename(subdir)
                print(f"Processing file: {csv_path}")

                wallet_allocations, total_allocation = process_csv_file(csv_path, wallet_addresses)

                if wallet_allocations:
                    result_dict[folder_name] = wallet_allocations
                    total_allocation_dict[folder_name] = f"{total_allocation:.12f}%"

    return result_dict, total_allocation_dict

def save_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def get_amount_your_wallets_in_protocols(data):
    results = {}
    for protocol in data:
        results[protocol] = len(data[protocol])
    return results

def main():
    wallet_addresses = read_wallets(wallets_file)
    result_dict, total_allocation_dict = process_all_files(root_dir, wallet_addresses)
    amount_wallets = get_amount_your_wallets_in_protocols(result_dict)
    save_to_json(result_dict, output_json_1)
    save_to_json(total_allocation_dict, output_json_2)
    save_to_json(amount_wallets, output_json_3)
    print(f"Results saved to {output_json_1}, {output_json_2}, and {output_json_3}")

if __name__ == "__main__":
    main()
