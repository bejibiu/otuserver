Otuserver
================
Project for training. Simple web server  uses asyncio with epoll. 
Add worksers by ThreadPool. 

Required
---------
* Python 3.7
* Centos 7


How install
------
Download project
```
git clone https://github.com/bejibiu/otuserver.git
``` 

Usege example
----------
##### For runs service in port `8000` 
```
python httpd.py --port 8000 
```
where `-p 8000` - option to set port BY DEFAULT `8000`

Other params
--------
|params|options|description|default|
|------|----|-----------|-------|
|host| --host |host address when run server| 127.0.0.1|
|port| --port |port listen|8000|
|file-log| --file-log|file to write log|None
|backlog|--backlog|backlog|100
|document-root| -r --document-root|root folder for server| work directory|
|workers| -w --workers| count ThreadPool| 1|

Docker 
----
To run server use docker:
```shell script
docker build -t otuserver .
docker run --rm -p 8000:8000 otuserver
```

Result apache benchmarks
```shell script
ab ab -n 50000 -c 100 -r http://localhost:8000/
``` 
 **without workers**  commit: *729aeb1* :

```shell script
Server Software:        Otuserver
Server Hostname:        localhost
Server Port:            8000

Document Path:          /
Document Length:        63 bytes

Concurrency Level:      100
Time taken for tests:   31.007 seconds
Complete requests:      50000
Failed requests:        0
Write errors:           0
Total transferred:      9950000 bytes
HTML transferred:       3150000 bytes
Requests per second:    1612.51 [#/sec] (mean)
Time per request:       62.015 [ms] (mean)
Time per request:       0.620 [ms] (mean, across all concurrent requests)
Transfer rate:          313.37 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       7
Processing:     9   62   8.0     59     140
Waiting:        2   62   8.0     59     140
Total:          9   62   8.0     59     140

Percentage of the requests served within a certain time (ms)
  50%     59
  66%     61
  75%     63
  80%     64
  90%     70
  95%     77
  98%     86
  99%     93
 100%    140 (longest request)
```
With worksers :
```shell script
Server Software:        Otuserver
Server Hostname:        localhost
Server Port:            8000

Document Path:          /
Document Length:        51 bytes

Concurrency Level:      100
Time taken for tests:   136.776 seconds
Complete requests:      50000
Failed requests:        0
Write errors:           0
Total transferred:      9350000 bytes
HTML transferred:       2550000 bytes
Requests per second:    365.56 [#/sec] (mean)
Time per request:       273.552 [ms] (mean)
Time per request:       2.736 [ms] (mean, across all concurrent requests)
Transfer rate:          66.76 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0       7
Processing:     6  273  25.1    268    1134
Waiting:        5  272  25.1    267    1133
Total:         13  273  25.1    268    1134

Percentage of the requests served within a certain time (ms)
  50%    268
  66%    275
  75%    280
  80%    284
  90%    299
  95%    315
  98%    346
  99%    371
 100%   1134 (longest request)
 ```