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
 **without workers** :

```shell script
Server Software:        Otuserver
Server Hostname:        localhost
Server Port:            8000

Document Path:          /
Document Length:        131 bytes

Concurrency Level:      100
Time taken for tests:   25.356 seconds
Complete requests:      50000
Failed requests:        0
Write errors:           0
Non-2xx responses:      50000
Total transferred:      13750000 bytes
HTML transferred:       6550000 bytes
Requests per second:    1971.90 [#/sec] (mean)
Time per request:       50.713 [ms] (mean)
Time per request:       0.507 [ms] (mean, across all concurrent requests)
Transfer rate:          529.56 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       4
Processing:     5   51   3.9     50      80
Waiting:        1   51   3.9     50      80
Total:          5   51   3.8     50      80

Percentage of the requests served within a certain time (ms)
  50%     50
  66%     50
  75%     51
  80%     52
  90%     54
  95%     58
  98%     62
  99%     68
 100%     80 (longest request)
```
With worksers :
```shell script
Server Software:        Otuserver
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /
Document Length:        131 bytes

Concurrency Level:      100
Time taken for tests:   42.582 seconds
Complete requests:      25000
Failed requests:        0
Write errors:           0
Non-2xx responses:      25000
Total transferred:      6875000 bytes
HTML transferred:       3275000 bytes
Requests per second:    587.10 [#/sec] (mean)
Time per request:       170.328 [ms] (mean)
Time per request:       1.703 [ms] (mean, across all concurrent requests)
Transfer rate:          157.67 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       6
Processing:     2  170  28.5    162     971
Waiting:        2  169  28.5    161     971
Total:          5  170  28.5    162     971

Percentage of the requests served within a certain time (ms)
  50%    162
  66%    168
  75%    173
  80%    177
  90%    195
  95%    228
  98%    253
  99%    274
 100%    971 (longest request)
 ```