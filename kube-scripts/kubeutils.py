#!/usr/bin/python3
#Author: babusankarv
#Description: support functions for Kubetool
################################################
from kubernetes import client, config
import json

class KubeUtils(object):
    
    def __init__(self, cluster):
        self.cluster = cluster
        self.configfile = "kubetool.config"
        with open(self.configfile) as file:
            data = json.load(file)
            cluster_configfile = data[cluster]
            file.close()
        config.load_kube_config(cluster_configfile)
    
    def connect(self): 
        client_con = client.CoreV1Api()
        return client_con
        
    def get_all_pods_allns(cluster_con):
        res = cluster_con.list_pod_for_all_namespaces(watch=False)
        for i in res.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    
    def get_all_pods(cluster_con, namespace):
        res = cluster_con.list_namespaced_pod(namespace,watch=False)
        for i in res.items:
            print("%s\t%s\t%s\t%s" % (i.status.pod_ip, i.status.phase, i.metadata.name, i.status.host_ip))
