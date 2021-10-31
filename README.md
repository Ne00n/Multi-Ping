# Multi-Ping

Uses data from https://github.com/Ne00n/Looking-Glass

![data mining](https://assets-cache0.moviebreak.de/system/bilder/story/photo/596dd05a6e73330b15070000/Multi_Pass1.jpg)

but with Pings

![data mining](https://thumbs.gfycat.com/MisguidedReasonableFulmar-max-1mb.gif)

Its magic, it gives you the closest providers with available services, based on latency.

**Examples**<br />

```
 curl -so- https://raw.githubusercontent.com/Ne00n/Multi-Ping/master/ping.py | python3
```

Could return you:
```
Fetching https://raw.githubusercontent.com/Ne00n/Looking-Glass/master/data/everything.json
fping 0 of 401
fping 100 of 401
fping 200 of 401
fping 300 of 401
fping 400 of 401
--- Top 10 ---
0.4ms (172.111.3.10) which is lg.nyc.maxkvm.net
0.8ms (107.191.96.26) which is lg.nyc.ramnode.com
1.4ms (104.206.82.24) which is nyc.lg.ssdblaze.com
1.4ms (8.8.8.8) which is lg.gcorelabs.com
1.4ms (172.111.48.4) which is lg.nyc.plox.host
1.7ms (91.132.1.132) which is lg.dc03.dedicontrol.com
1.8ms (185.213.26.26) which is lg.ny.hosthatch.com
1.8ms (195.123.233.46) which is lg-us2.isplevel.com
1.9ms (107.161.50.42) which is nyc.lg.webhorizon.in
2.0ms (192.3.165.30) which is lg-nj.racknerd.com
2.0ms (198.46.189.4) which is nj.lg.virmach.com
-- Results ---
```
