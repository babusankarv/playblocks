#!/usr/bin/python3
#Author: babusankarv
#Description: Tool to interact with Kube cluster
################################################
import sys
import argparse
from kubeutils import KubeUtils as ku

def command_parse(sys_argv):
    parser = argparse.ArgumentParser(description='kube tool')
    commands = parser.add_subparsers(dest='operation')

    create_parser = commands.add_parser("create")
    create_parser.add_argument("--namespace", help="namespace", default="default")
    create_parser.add_argument("--cluster", help="cluster", default="local")

    get_parser = commands.add_parser("get")
    get_parser.add_argument("--objectname", help="k8s object name")
    get_parser.add_argument("--namespace", help="namespace", default="default")
    get_parser.add_argument("--cluster", help="cluster", default="local")
    
    update_parser = commands.add_parser("update")
    update_parser.add_argument("--namespace", help="namespace", default="default")
    update_parser.add_argument("--cluster", help="cluster", default="local")
    args = parser.parse_args()
    return args



def main(sys_args):
    args = command_parse(sys_args)
    my_cluster = ku(args.cluster)
    my_cluster_con = my_cluster.connect()
    
    if args.operation == 'get':
        if (args.objectname == 'pods' and args.namespace == "all"):
            ku.get_all_pods_allns(my_cluster_con)
        elif(args.objectname == 'pods'):
            ku.get_all_pods(my_cluster_con, args.namespace)
    elif (args.operation == 'update'):
        print('update operations')
    elif (args.operation == 'create'):
        print('create operations')
    else:
        print('unrecognized command')
        print('usage: ./kubetool -h')
        exit(1)
        

if __name__ == '__main__':
    main(sys.argv)
