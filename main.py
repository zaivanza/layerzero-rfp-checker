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
        return None

def find_allocation_column(headers):
    allocation_list = [
        'Allocation', 
        'final_share', 
        'Allocation %', 
        '% Allocation', 
        'Allocation (%)',
        'Allocation % ',
        'RFP Allocation',
        
        ]
    for header in allocation_list:
        if header in headers:
            return headers.index(header)
    return None

def process_csv_file(csv_path, wallet_addresses):
    wallet_allocations = {}
    total_allocation = 0.0

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        allocation_idx = find_allocation_column(headers)
        if allocation_idx is None:
            print(f"No 'Allocation' header in file: {csv_path}")
            return wallet_allocations, total_allocation
        
        for row in reader:
            if not any(row):
                continue
            try:
                address = row[0].strip().lower()
    
                if address in wallet_addresses:
                    allocation_value = parse_allocation(row[allocation_idx])
                    if allocation_value is not None:
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
        folder_name = os.path.basename(subdir)
        folder_wallet_allocations = {}
        folder_total_allocation = 0.0

        for file in files:
            if file.endswith('.csv'):
                csv_path = os.path.join(subdir, file)
                print(f"Processing file: {csv_path}")

                wallet_allocations, total_allocation = process_csv_file(csv_path, wallet_addresses)

                for addr, alloc in wallet_allocations.items():
                    if addr in folder_wallet_allocations:
                        folder_wallet_allocations[addr] += float(alloc.rstrip('%'))
                    else:
                        folder_wallet_allocations[addr] = float(alloc.rstrip('%'))
                
                folder_total_allocation += total_allocation
        
        if folder_wallet_allocations:
            result_dict[folder_name] = {addr: f"{alloc:.12f}%" for addr, alloc in folder_wallet_allocations.items()}
            total_allocation_dict[folder_name] = f"{folder_total_allocation:.12f}%"

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
