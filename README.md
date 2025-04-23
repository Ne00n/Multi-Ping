# Multi-Ping

Uses data from https://data.neoon.net/

![multipass](https://assets-cache0.moviebreak.de/system/bilder/story/photo/596dd05a6e73330b15070000/Multi_Pass1.jpg)

but with Pings

![one ping](https://media.licdn.com/dms/image/C5622AQENhqeHj7AaRw/feedshare-shrink_2048_1536/0/1626309747501?e=2147483647&v=beta&t=_a-JghvePLBqr-W6LC0j9_C3fEg9rkMSuKuHn2dWt1Q)

Its magic, it gives you the closest providers with available services, based on latency.

**Params**<br />

```
 -c Amount of Pings, Default 1
 -p Batch Size, Default 100
 -a ASN Selector, Default Any
```

**Examples**<br />

```
 curl -so- https://raw.githubusercontent.com/Ne00n/Multi-Ping/master/ping.py | python3
 curl -so- https://raw.githubusercontent.com/Ne00n/Multi-Ping/master/ping.py | python3 - -c15
 curl -so- https://raw.githubusercontent.com/Ne00n/Multi-Ping/master/ping.py | python3 - -p10 -c15
```
![data mining](https://i.imgur.com/vNn79Qc.gif)
