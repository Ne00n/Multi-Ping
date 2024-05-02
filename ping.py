import urllib.request, subprocess, json, time, sys, re

pings = 1
batchSize = 100
mode = "ipv4"
target = ""

if len(sys.argv) >= 2:
    args = re.findall("((-c|-p|-l)\s?([0-9A-Za-z]+)|-6)",' '.join(sys.argv[1:]))
    for arg in args:
        if arg[1] == "-c": pings = float(arg[2])
        if arg[1] == "-p": batchSize = int(arg[2])
        if arg[1] == "-l": target = arg[2]
        if arg[0] == "-6": mode = "ipv6"

print("Please select a source file")
print("1: Looking-Glass, old but larger")
print("2: Looking-Glass-2, new but smoler")
sourceFile = input("Please input either 1 or 2: ")

if sourceFile == "2":
    file = "https://raw.githubusercontent.com/Ne00n/Looking-Glass-2/master/data/everything.json"
else:
    file = "https://raw.githubusercontent.com/Ne00n/Looking-Glass/master/data/everything.json"

def error(run):
    print(f"Retrying {run+1} of 4")
    if run == 3:
        print("Aborting, limit reached.")
        exit()
    time.sleep(2)

for run in range(4):
    try:
        print(f"Fetching {file}")
        request = urllib.request.urlopen(file, timeout=3)
        if (request.getcode() == 200):
            raw = request.read().decode('utf-8')
            json = json.loads(raw)
            break
        else:
            print("Got non 200 response code")
            error(run)
    except Exception as e:
        print(f"Error {e}")
        error(run)

targets,count,mapping = [],0,{}
for domain,lgs in json.items():
    for lg,ip in lgs.items():
        if ip:
            for ip,location in ip[mode].items():
                mapping[ip] = {}
                if target == "" or target in location:
                    mapping[ip] = {"domain":domain,"lg":lg,"geo":location}
                    targets.append(ip)

results = ""
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

result,top = [],15
result.append("Latency\tIP address\tDomain\tLocation (Maxmind)\tLooking Glass")
result.append("-------\t-------\t-------\t-------\t-------")
for index,ip in enumerate(sorted.items()):
    data = mapping[ip[0]]
    result.append(f"{ip[1]}ms\t{ip[0]}\t{data['domain']}\t{data['geo']}\t{data['lg']}")
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
