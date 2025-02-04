#!/usr/bin/env python3

import subprocess
import json
import ipaddress
import argparse

def get_pod_ip_address():
    """Runs 'kubectl get pods --all-namespaces -o json' and extracts pod IPs."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "--all-namespaces", "-o", "json"],
            stderr=subprocess.PIPE, universal_newlines=True, check=True
        )
        pod_data = json.loads(result.stdout)
        
        pod_ips = []
        for item in pod_data.get("items", []):
            namespace = item["metadata"]["namespace"]
            pod_name = item["metadata"]["name"]
            pod_ip = item.get("status", {}).get("podIP")

            if pod_ip:
                pod_ips.append({"namespace": namespace, "pod": pod_name, "ip": pod_ip})

        return pod_ips

    except subprocess.CalledProcessError as e:
        print(f"Error running kubectl command: {e}")
        return []

def check_global_collisions(pod_ips):
    """Checks for IP collisions across all namespaces."""
    networks = set()
    collisions = set()

    for pod in pod_ips:
        ip_net = ipaddress.ip_network(f"{pod['ip']}/24", strict=False)
        if any(ip_net.overlaps(n) for n in networks):
            collisions.add(str(ip_net))
        networks.add(ip_net)

    if collisions:
        print("Global IP Collisions Found:")
        for collision in collisions:
            print(f" - {collision}")
    else:
        print("No Global IP Collisions Detected")

def check_namespace_collisions(pod_ips):
    """Checks for IP collisions within each namespace separately."""
    namespace_networks = {}
    namespace_collisions = {}

    for pod in pod_ips:
        namespace = pod["namespace"]
        ip_net = ipaddress.ip_network(f"{pod['ip']}/24", strict=False)

        if namespace not in namespace_networks:
            namespace_networks[namespace] = set()

        # Check for collisions within the same namespace
        if any(ip_net.overlaps(n) for n in namespace_networks[namespace]):
            if namespace not in namespace_collisions:
                namespace_collisions[namespace] = set()
            namespace_collisions[namespace].add(str(ip_net))

        namespace_networks[namespace].add(ip_net)

    if namespace_collisions:
        print("⚠️ Namespace-Specific IP Collisions Found:")
        for ns, collisions in namespace_collisions.items():
            print(f"Namespace: {ns}")
            for collision in collisions:
                print(f" - {collision}")
    else:
        print("No Namespace-Specific IP Collisions Detected")

def check_collisions_from_file(file_path):
    """Checks for IP collisions from a file containing a list of IPs/subnets."""
    try:
        with open(file_path, "r") as f:
            ip_list = [line.strip() for line in f.readlines() if line.strip()]
        
        networks = set()
        collisions = set()

        for ip in ip_list:
            try:
                ip_net = ipaddress.ip_network(ip, strict=False)
                if any(ip_net.overlaps(n) for n in networks):
                    collisions.add(str(ip_net))
                networks.add(ip_net)
            except ValueError:
                print(f"Invalid IP or subnet format: {ip}")

        if collisions:
            print("Collisions Found in File:")
            for collision in collisions:
                print(f" - {collision}")
        else:
            print("No Collisions Found in File")

    except FileNotFoundError:
        print(f"File not found: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Check for Kubernetes pod IP collisions.")
    
    parser.add_argument("--mode", choices=["global", "namespace"], default="global",
                        help="Mode of collision check: 'global' (default) or 'namespace'.")
    
    parser.add_argument("--check-collision", metavar="<file_path>",
                        help="Check collisions from a file containing a list of IPs/subnets.")

    args = parser.parse_args()

    if args.check_collision:
        check_collisions_from_file(args.check_collision)
    else:
        pod_ips = get_pod_ip_address()

        if not pod_ips:
            print("No pod IPs found. Ensure Kubernetes cluster is running and accessible.")
            return

        if args.mode == "global":
            check_global_collisions(pod_ips)
        elif args.mode == "namespace":
            check_namespace_collisions(pod_ips)

    

if __name__ == "__main__":
    main()
