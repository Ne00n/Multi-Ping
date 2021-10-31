import subprocess, requests, json, re

def getLG(target):
    for domain,lgs in json.items():
        for lg,ip in lgs.items():
            if ip and ip['ipv4'] == target: return lg

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
    if ms is "NaN": ms = 900
    if ip not in results: results[ip] = float(ms)

sorted = {k: results[k] for k in sorted(results, key=results.get)}

print("--- Top 10 ---")
for index,ip in enumerate(sorted.items()):
    lg = getLG(ip[0])
    print(f"{ip[1]}ms ({ip[0]}) which is {lg}")
    if index == 10: break
print("-- Results ---")
