package main

import (
	"context"
	"flag"
	"fmt"
	//"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"os"
	"path/filepath"
)

func main() {
	var kubeconfig *string
	var ns, label, field string
	if home := homeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "absolute path to config file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to kubeconfig file")
	}
	flag.StringVar(&ns, "ns", "", "namespace")
	flag.StringVar(&label, "label", "", "Label Selector")
	flag.StringVar(&field, "field", "", "Field Selector")
	flag.Parse()

	// use the current context in kubeconfig
	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
	if err != nil {
		panic(err.Error())
	}

	//create clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	//create API connection
	kubeapi := clientset.CoreV1()

	//Set List Options
	listOptions := metav1.ListOptions{
		LabelSelector: label,
		FieldSelector: field,
	}

	//Get Pod details
	pods, err := kubeapi.Pods(ns).List(context.TODO(), listOptions)
	if err != nil {
		panic(err.Error())
	}
	fmt.Printf("There are %d pods in the cluster in namespace %s\n", len(pods.Items), ns)
	fmt.Printf("%-40s%-10s%-15s%-20s%-15s\n", "PodName", "PodStatus", "PodIP", "NodeName", "NodeIP")
	for _, pod := range pods.Items {
		fmt.Printf("%-40s%-10s%-15s%-20s%-15s\n", pod.Name, pod.Status.Phase, pod.Status.PodIP, pod.Spec.NodeName, pod.Status.HostIP)
	}
}

func homeDir() string {
	if h := os.Getenv("HOME"); h != "" {
		return h
	}
	return os.Getenv("USERPROFILE") // windows
}
