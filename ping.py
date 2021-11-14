import subprocess, requests, json, sys, re

pings = 1
batchSize = 100
mode = "ipv4"

if len(sys.argv) >= 2:
    args = re.findall("((-c|-p)\s?([0-9]+)|-6)",' '.join(sys.argv[1:]))
    for arg in args:
        if arg[1] == "-c": pings = float(arg[2])
        if arg[1] == "-p": batchSize = int(arg[2])
        if arg[0] == "-6": mode = "ipv6"

file = "https://raw.githubusercontent.com/Ne00n/Looking-Glass/master/data/everything.json"
print(f"Fetching {file}")

raw = requests.get(file,allow_redirects=False,timeout=3)
json = json.loads(raw.text)

targets,count,mapping = [],0,{}
for domain,lgs in json.items():
    for lg,ip in lgs.items():
        if ip:
            for ip in ip[mode]:
                targets.append(ip)
                mapping[ip] = {}
                mapping[ip] = {"domain":domain,"lg":lg}

results = ""
while count <= len(targets):
    print(f"fping {count} of {len(targets)}")
    batch = ' '.join(targets[count:count+batchSize])
    p = subprocess.run(f"fping -c {pings} {batch}", stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if "command not found" in p.stdout.decode('utf-8'):
        print("Please install fping")
        exit()
    results += p.stdout.decode('utf-8')
    count += batchSize

parsed = re.findall("([0-9.:a-z]+).*?([0-9]+.[0-9]+|NaN).*?([0-9])% loss",results, re.MULTILINE)
results = {}
for ip,ms,loss in parsed:
    if ms == "NaN": ms = 900
    if ip not in results: results[ip] = float(ms)

sorted = {k: results[k] for k in sorted(results, key=results.get)}

result,top = [],10
for index,ip in enumerate(sorted.items()):
    data = mapping[ip[0]]
    result.append(f"{ip[1]}ms\t({ip[0]})\t{data['domain']}\t({data['lg']})")
    if float(ip[1]) < 15 and index == top: top += 1
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
print(f"--- Top {top} ---")
print(result)
print("-- Results ---")
