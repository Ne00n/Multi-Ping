import subprocess, requests, json, re

def getLG(target):
    for domain,lgs in json.items():
        for lg,ip in lgs.items():
            if ip and ip['ipv4'] == target: return [domain,lg]

file = "https://raw.githubusercontent.com/Ne00n/Looking-Glass/master/data/everything.json"
print(f"Fetching {file}")

raw = requests.get(file,allow_redirects=False,timeout=3)
json = json.loads(raw.text)

targets,count = [],0
for domain,lgs in json.items():
    for lg,ip in lgs.items():
        if ip: targets.append(ip['ipv4'])

results = ""
while count <= len(targets):
    print(f"fping {count} of {len(targets)}")
    batch = ' '.join(targets[count:count+100])
    p = subprocess.run(f"fping -c 1 {batch}", stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if "command not found" in p.stdout.decode('utf-8'):
        print("Please install fping")
        exit()
    results += p.stdout.decode('utf-8')
    count += 100

parsed = re.findall("([0-9.]+).*?([0-9]+.[0-9]+|NaN).*?([0-9])% loss",results, re.MULTILINE)
results = {}
for ip,ms,loss in parsed:
    if ms == "NaN": ms = 900
    if ip not in results: results[ip] = float(ms)

sorted = {k: results[k] for k in sorted(results, key=results.get)}

result = []
for index,ip in enumerate(sorted.items()):
    data = getLG(ip[0])
    result.append(f"{ip[1]}ms ({ip[0]}) which is {data[0]} ({data[1]})")
    if index == 10: break

def formatTable(list):
    longest,response = {},""
    for row in list:
        elements = row.split()
        for index, entry in enumerate(elements):
            if not index in longest: longest[index] = 0
            if len(entry) > longest[index]: longest[index] = len(entry)
    for i, row in enumerate(list):
        elements = row.split()
        for index, entry in enumerate(elements):
            if len(entry) < longest[index]:
                diff = longest[index] - len(entry)
                while len(entry) < longest[index]:
                    entry += " "
            response += f" {entry}"
        if i < len(list) -1: response += "\n"
    return response

result = formatTable(result)
print("--- Top 10 ---")
print(result)
print("-- Results ---")
