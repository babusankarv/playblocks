#!/usr/bin/python3
#Author: babusankarv
#Description: Tool to interact with Kube cluster
#########
import sys
import argparse
from kubernetes import client, config

def command_parse(sys_argv):
    parser = argparse.ArgumentParser(description='kube tool')
    commands = parser.add_subparsers(dest='operation')

    create_parser = commands.add_parser("create")

    get_parser = commands.add_parser("get")
    get_parser.add_argument("--objectname", help="k8s object name")

    update_parser = commands.add_parser("update")
    args = parser.parse_args()
    return args



def main(sys_args):
    args = command_parse(sys_args)
    
    if args.operation == 'get':
        config.load_kube_config()
        api = client.CoreV1Api()
        res = api.list_pod_for_all_namespaces(watch=False)
        for i in res.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    elif args.operation == 'update':
        print('update operations')
    elif args.operation == 'create':
        print('create operations')
    else:
        print('unrecognized command')
        print('usage: ./kubetool -h')
        exit(1)
        

if __name__ == '__main__':
    main(sys.argv)
