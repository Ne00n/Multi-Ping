import urllib.request, subprocess, random, json, time, sys, re, tempfile, os
import csv

pings = 1
batchSize = 100
targetASN = ""
everything = False
jsonOutput = False

if len(sys.argv) >= 2:
    args = re.findall("((-c|-p|-a)\s?([0-9A-Za-z]+)|-e|-j)",' '.join(sys.argv[1:]))
    for arg in args:
        if arg[1] == "-c": pings = float(arg[2])
        if arg[1] == "-p": batchSize = int(arg[2])
        if arg[1] == "-a": targetASN = arg[2]
        if arg[0] == "-e": everything = True
        if arg[0] == "-j": jsonOutput = True

file = "https://data.neoon.net/pingable.min.min.jsonl"

def error(run):
    print(f"Retrying {run+1} of 4")
    if run == 3:
        print("Aborting, limit reached.")
        exit()
    time.sleep(2)

# Create a temporary file to store the downloaded content
temp_file = None
for run in range(4):
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp_file:
            with urllib.request.urlopen(file, timeout=3) as response:
                if response.getcode() == 200:
                    print(f"Downloading {file}")
                    chunk_size = 8192
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        temp_file.write(chunk)
                    temp_filename = temp_file.name
                    break
                else:
                    print("Got non 200 response code")
                    error(run)
    except Exception as e:
        print(f"Error {e}")
        error(run)
        if temp_file:
            try:
                os.unlink(temp_file.name)
                temp_file = None
            except:
                pass

if not temp_file:
    print("Failed to download file after multiple attempts")
    exit()

try:
    print(f"Reading {file}")
    with open(temp_filename, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        with open('targets.txt', 'w', encoding='utf-8') as targets_file:
            for line in f:
                jData = json.loads(line)
                for asn, data in jData.items():
                    if targetASN != "" and asn != targetASN: continue
                    for firstOctet, firstLayer in data.items():
                        for secondOctet, secondLayer in firstLayer.items():
                            for thirdOctet, ips in secondLayer.items():
                                subnet = f"{firstOctet}.{secondOctet}.{thirdOctet}"
                                ip = random.choice(ips)
                                ip = f"{subnet}.{ip}"
                                targets_file.write(f"{ip}\t{asn}\n")  # Write IP and ASN together
                                if not everything: break
                            if not everything: break
                        if not everything: break
finally:
    try:
        os.unlink(temp_filename)
    except:
        pass

# Count total targets first
total_targets = 0
with open('targets.txt', 'r', encoding='utf-8') as f:
    total_targets = sum(1 for _ in f)

# Initialize results CSV file with ASN column
results_csv = 'results.csv'
with open(results_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['ip', 'asn', 'latency'])

# Process targets from file in batches
processed = 0
with open('targets.txt', 'r', encoding='utf-8') as targets_file:
    while True:
        batch = []
        ip_asn_map = {}  # Store IP to ASN mapping for this batch
        for _ in range(batchSize):
            line = targets_file.readline().strip()
            if not line:
                break
            ip, asn = line.split('\t')
            batch.append(ip)
            ip_asn_map[ip] = asn
        
        if not batch:
            break
            
        print(f"fping {min(processed + len(batch), total_targets)} of {total_targets}")
        batch_str = ' '.join(batch)
        p = subprocess.run(f"fping -c {pings} {batch_str}", stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        if not p.stdout.decode('utf-8'):
            print("Please install fping (apt-get install fping / yum install fping)")
            exit()
        
        # Parse and save results immediately with ASN
        output = p.stdout.decode('utf-8')
        parsed = re.findall("([0-9.:a-z]+).*?([0-9]+.[0-9]+|NaN).*?([0-9])% loss", output, re.MULTILINE)
        
        with open(results_csv, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for ip, ms, loss in parsed:
                if ms == "NaN": ms = 900
                asn = ip_asn_map.get(ip, "UNKNOWN")
                writer.writerow([ip, asn, float(ms)])
        
        processed += len(batch)

# Clean up targets file
try:
    os.remove('targets.txt')
except:
    pass

# Read and process results from CSV
results = {}
with open(results_csv, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        ip, asn, latency = row
        results[ip] = {'latency': float(latency), 'asn': asn}

sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1]['latency'])}

# Prepare output
result, top = [], 50
result_json = {}

result.append("Latency\tIP\tASN")
result.append("-------\t-------\t-------")
for index, (ip, data) in enumerate(sorted_results.items()):
    asn = data['asn']
    latency = data['latency']
    result.append(f"{latency}ms\t{ip}\tAS{asn}")
    
    if asn not in result_json:
        result_json[asn] = []
    result_json[asn].append({
        "ip": ip,
        "latency": latency
    })
    
    if float(latency) < 20 and index == top: top += 1
    if index == top: break

def formatTable(list):
    longest, response = {}, ""
    for row in list:
        elements = row.split("\t")
        for index, entry in enumerate(elements):
            if not index in longest: longest[index] = 0
            if len(entry) > longest[index]: longest[index] = len(entry)
    for i, row in enumerate(list):
        elements = row.split("\t")
        for index, entry in enumerate(elements):
            if len(entry) < longest[index]:
                while len(entry) < longest[index]:
                    entry += " "
            response += f"{entry}" if response.endswith("\n") or response == "" else f" {entry}"
        if i < len(list) - 1: response += "\n"
    return response

if jsonOutput:
    output_filename = "pings.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, indent=2)
    print(f"\nResults saved to {output_filename}")

result = formatTable(result)
print(f"\nTop {top}")
print(result)

# Clean up results CSV
try:
    os.remove(results_csv)
except:
    pass