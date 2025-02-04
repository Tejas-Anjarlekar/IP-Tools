# IP-Tools
To explore IP range collisions in Kubernetes cluster.

We have created simple python script which will get deployed using Docker container considering on same host server where Kubernetes cluster is running.
It will try to connect k8 cluster using `kubectl` command and get pod details using `--all-namespaces`.
Once connected successfully it will parse the `json` response and get IP / Networking details and used `ipaddress` library it will check for overlapping of networks by default for all namespces.
Using Flag `--mode namespace` it will check for isolates namespaces.

### Note:

```shell
- This tool is deveoloped on Oraclelinux:8 docker image which uses python3.6 as a default version.
```
### Libraries Used:

For main script `ip_tools.py`:

```shell
import subprocess
import json
import ipaddress
import argparse
```
For Unit test script `test_ip_tools.py`:

```shell
import unittest
from unittest.mock import patch, mock_open, MagicMock
import subprocess
```

For `Dockerfile.test`:

```shell
python3 python3-pip && \
pip3 install --upgrade pip && \
pip3 install coverage
```
For `Dockerfile`:

```shell
python3 python3-pip 
kubectl
```

### Steps to execute the Tool:

- Clone the git repo into your host where docker container needs to be deployed:

```shell
git clone https://github.com/Tejas-Anjarlekar/IP-Tools.git
cd Ip-Tools
```

- As we are having `Makfile` targest already defined to run unit test cases inside docker container as well as to deploy container which executes main script.


```shell
make run-test

===========================================================
........Error running kubectl command: Command 'kubectl get pods --all-namespaces -o json' returned non-zero exit status 1.
File not found: non_existent_file.txt

----------------------------------------------------------------------
Ran 8 tests in 0.017s

OK
Name          Stmts   Miss  Cover
---------------------------------
ip_tools.py      90     25    72%
---------------------------------
TOTAL            90     25    72%
===========================================================

Test cases covered:
test_get_pod_ip_address – Mocks kubectl get pods and verifies IP extraction.
test_check_global_collisions_no_collision – No overlapping networks.
test_check_global_collisions_detected – Overlapping networks exist.
test_check_namespace_collisions_no_collision – No overlaps within namespaces.
test_check_namespace_collisions_detected – Overlapping networks within a namespace.
test_check_collisions_from_file_no_collision – Reads a file and checks for no collisions.
test_check_collisions_from_file_detected – Detects overlapping networks from a file.
test_called_process_error - Error running kubectl commands using subprocess.
```

- To run script by passing `--check-collision` flag along with file_path for file containing ip lists.

```shell
make run-iptool-script using FILE=/app/ip-list.txt
===========================================================

Sample Output:

Running with --check-collision /app/ip-list.txt...
Collisions Found in File:
 - 192.168.2.0/24
 - 192.168.1.0/24
 - 10.0.0.0/8
 - 172.16.0.0/16
docker system prune -f
Total reclaimed space: 0B
```
- Since we have assumed that kubernete cluster is running and when we deploy this script in live cluster it will give actual list of overlapping ip networks.

- For now, we are getting expected error that K8 cluster is not running.

- Below output for executing script without passing `--check-collision` flag and static file.

```shell
make run-iptool-script
===========================================================

Error running kubectl command: Command '['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'json']' returned non-zero exit status 1.
No pod IPs found. Ensure Kubernetes cluster is running and accessible.
docker system prune -f
```