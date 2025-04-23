import urllib.request, subprocess, random, json, time, sys, re

pings = 1
batchSize = 100
targetASN = ""
everything = False

if len(sys.argv) >= 2:
    args = re.findall("((-c|-p|-a)\s?([0-9A-Za-z]+)|-e)",' '.join(sys.argv[1:]))
    for arg in args:
        if arg[1] == "-c": pings = float(arg[2])
        if arg[1] == "-p": batchSize = int(arg[2])
        if arg[1] == "-a": targetASN = arg[2]
        if arg[0] == "-e": everything = True

file = "https://data.neoon.net/pingable.min.min.jsonl"

def error(run):
    print(f"Retrying {run+1} of 4")
    if run == 3:
        print("Aborting, limit reached.")
        exit()
    time.sleep(2)

targets,mapping = [],{}
for run in range(4):
    try:
        print(f"Fetching {file}")
        request = urllib.request.urlopen(file, timeout=3)
        if (request.getcode() == 200):
            print(f"Loading {file}")
            raw = request.read().decode('utf-8')
            lines = raw.strip().split('\n')
            for index, line in enumerate(lines):
                if index == 0: continue
                jData = json.loads(line)
                for asn,data in jData.items():
                    if targetASN != "" and asn != targetASN: continue
                    for firstOctet, firstLayer in data.items():
                        for secondOctet, secondLayer in firstLayer.items():
                            for thirdOctet, ips in secondLayer.items():
                                subnet = f"{firstOctet}.{secondOctet}.{thirdOctet}"
                                ip = random.choice(ips)
                                ip = f"{subnet}.{ip}"
                                mapping[ip] = {"asn":asn}
                                targets.append(ip)
                                if not everything: break
                            if not everything: break
                        if not everything: break
            break
        else:
            print("Got non 200 response code")
            error(run)
    except Exception as e:
        print(f"Error {e}")
        error(run)

raw = {}
results,count = "",0
while count <= len(targets):
    print(f"fping {count} of {len(targets)}")
    batch = ' '.join(targets[count:count+batchSize])
    if not batch: break
    p = subprocess.run(f"fping -c {pings} {batch}", stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if not p.stdout.decode('utf-8'):
        print("Please install fping (apt-get install fping / yum install fping)")
        exit()
    results += p.stdout.decode('utf-8')
    count += batchSize

parsed = re.findall("([0-9.:a-z]+).*?([0-9]+.[0-9]+|NaN).*?([0-9])% loss",results, re.MULTILINE)
results = {}
for ip,ms,loss in parsed:
    if ms == "NaN": ms = 900
    if ip not in results: results[ip] = float(ms)

sorted = {k: results[k] for k in sorted(results, key=results.get)}

result,top = [],50
result.append("Latency\tIP\tASN")
result.append("-------\t-------\t-------")
for index,ip in enumerate(sorted.items()):
    data = mapping[ip[0]]
    result.append(f"{ip[1]}ms\t{ip[0]}\tAS{data['asn']}")
    if float(ip[1]) < 20 and index == top: top += 1
    if index == top: break

def formatTable(list):
    longest,response = {},""
    for row in list:
        elements = row.split("\t")
        for index, entry in enumerate(elements):
            if not index in longest: longest[index] = 0
            if len(entry) > longest[index]: longest[index] = len(entry)
    for i, row in enumerate(list):
        elements = row.split("\t")
        for index, entry in enumerate(elements):
            if len(entry) < longest[index]:
                diff = longest[index] - len(entry)
                while len(entry) < longest[index]:
                    entry += " "
            response += f"{entry}" if response.endswith("\n") or response == "" else f" {entry}"
        if i < len(list) -1: response += "\n"
    return response

result = formatTable(result)
print(f"\nTop {top}")
print(result)
