import os
import csv
import json

wallets_file = 'wallets.txt'
root_dir = 'RFP Allocations'
output_json_1 = 'result_1.json'
output_json_2 = 'result_2.json'

def read_wallets(file_path):
    with open(file_path, 'r') as f:
        return {line.strip().lower() for line in f}

def process_csv_file(csv_path, wallet_addresses):
    wallet_allocations = {}
    total_allocation = 0.0

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not any(row):
                continue
            try:
                address = row[0].strip().lower()
                allocation = row[1].strip()
                if address in wallet_addresses:
                    allocation_value = float(allocation.rstrip('%'))
                    wallet_allocations[address] = allocation
                    total_allocation += allocation_value
            except (IndexError, ValueError) as e:
                print(f"Error processing row: {row}, error: {e}")
                continue

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

def main():
    wallet_addresses = read_wallets(wallets_file)
    result_dict, total_allocation_dict = process_all_files(root_dir, wallet_addresses)
    save_to_json(result_dict, output_json_1)
    save_to_json(total_allocation_dict, output_json_2)
    print(f"Results saved to {output_json_1} and {output_json_2}")

if __name__ == "__main__":
    main()
