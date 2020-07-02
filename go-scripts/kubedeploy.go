package main

import (
	"context"
	"flag"
	"fmt"
	//"k8s.io/apimachinery/pkg/api/errors"
	appsv1 "k8s.io/api/apps/v1"
	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	retry "k8s.io/client-go/util/retry"
	"os"
	"path/filepath"
)

func main() {
	var (
		kubeconfig                      *string
		ns, label, field, object, image string
		rc                              int
	)
	if home := homeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "absolute path to config file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to kubeconfig file")
	}
	//flag.StringVar(&action, "action", "", "Action - get,create,update")
	//sub commands based on action key-word
	getAction := flag.NewFlagSet("get", flag.ExitOnError)
	createAction := flag.NewFlagSet("create", flag.ExitOnError)
	updateAction := flag.NewFlagSet("update", flag.ExitOnError)
	deleteAction := flag.NewFlagSet("delete", flag.ExitOnError)
	//flag pointers for get
	getAction.StringVar(&object, "object", "", "kube object - pod,deployment,service")
	getAction.StringVar(&ns, "ns", "", "namespace")
	getAction.StringVar(&field, "field", "", "Field Selector")
	getAction.StringVar(&label, "label", "", "Label Selector")
	//flag pointers for create
	createAction.StringVar(&object, "object", "", "kube object - pod,deployment,service")
	createAction.StringVar(&ns, "ns", "", "namespace")
	createAction.StringVar(&label, "label", "", "Label Selector")
	//flag pointers for update
	updateAction.StringVar(&object, "object", "", "kube object - pod,deployment,service")
	updateAction.StringVar(&ns, "ns", "", "namespace")
	updateAction.StringVar(&label, "label", "", "Label Selector")
	updateAction.StringVar(&image, "image", "", "image name")
	updateAction.IntVar(&rc, "rc", 2, "replica rount")
	//flag pointers for delete
	deleteAction.StringVar(&object, "object", "", "kube object - pod,deployment,service")
	deleteAction.StringVar(&ns, "ns", "", "namespace")
	deleteAction.StringVar(&label, "label", "", "Label Selector")
	//check for action keyword
	if len(os.Args) < 2 {
		fmt.Println("one action key word required - get,create,update,delete")
		os.Exit(1)
	}

	//parse flag arguments based on the action keyword
	switch os.Args[1] {
	case "get":
		getAction.Parse(os.Args[2:])
	case "create":
		createAction.Parse(os.Args[2:])
	case "update":
		updateAction.Parse(os.Args[2:])
	case "delete":
		deleteAction.Parse(os.Args[2:])
	default:
		flag.PrintDefaults()
		os.Exit(1)
	}

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

	if getAction.Parsed() {
		if object == "pod" {
			getPodDetails(clientset, ns, label, field)
		}
	} else if createAction.Parsed() {
		if object == "deployment" {
			createDeployment(clientset, ns, label)
		} else if object == "pod" {
			createPod(clientset, ns, label)
		}
	} else if updateAction.Parsed() {
		if object == "deployment" {
			updateDeployment(clientset, rc, ns, label, image)
		}
	} else if deleteAction.Parsed() {
		if object == "deployment" {
			deleteDeployment(clientset, ns, label)
		} else if object == "pod" {
			deletePod(clientset, ns, label)
		}
	} else {
		fmt.Println("missing action keyword")
	}

}

func homeDir() string {
	if h := os.Getenv("HOME"); h != "" {
		return h
	}
	return os.Getenv("USERPROFILE") // windows
}

func getPodDetails(clientset *kubernetes.Clientset, ns, label, field string) {
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

func createDeployment(clientset *kubernetes.Clientset, ns, label string) {
	//create API connection
	kubeapi := clientset.AppsV1().Deployments(ns)

	//create deployment spec
	deployment := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name: label + "-web",
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: int32Ptr(2),
			Selector: &metav1.LabelSelector{
				MatchLabels: map[string]string{
					"app": label,
				},
			},
			Template: apiv1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: map[string]string{
						"app": label,
					},
				},
				Spec: apiv1.PodSpec{
					Containers: []apiv1.Container{
						{
							Name:  "web",
							Image: "nginx:1.12",
							Ports: []apiv1.ContainerPort{
								{
									Name:          "http",
									Protocol:      apiv1.ProtocolTCP,
									ContainerPort: 80,
								},
							},
						},
					},
				},
			},
		},
	}
	fmt.Println("Creating Deployment...")
	result, err := kubeapi.Create(context.TODO(), deployment, metav1.CreateOptions{})
	if err != nil {
		panic(err)
	}
	fmt.Printf("Created deployment %q.\n", result.GetObjectMeta().GetName())
}

func updateDeployment(clientset *kubernetes.Clientset, rc int, ns, label, image string) {
	//create API connection
	kubeapi := clientset.AppsV1().Deployments(ns)
	//check for deployment object existance before update
	retryErr := retry.RetryOnConflict(retry.DefaultRetry, func() error {
		result, getErr := kubeapi.Get(context.TODO(), label+"-web", metav1.GetOptions{})
		if getErr != nil {
			panic(fmt.Errorf("Failed to get latest version of Deployment: %v", getErr))
		}
		m := int32(rc)
		result.Spec.Replicas = int32Ptr(m)                    // change replica count
		result.Spec.Template.Spec.Containers[0].Image = image // change nginx version
		_, updateErr := kubeapi.Update(context.TODO(), result, metav1.UpdateOptions{})
		return updateErr
	})
	if retryErr != nil {
		panic(fmt.Errorf("update failed: %v", retryErr))
	}
	fmt.Println("updated deployment")
}

func deleteDeployment(clientset *kubernetes.Clientset, ns, label string) {
	//create API connection
	kubeapi := clientset.AppsV1().Deployments(ns)
	//set delete policy
	deletePolicy := metav1.DeletePropagationForeground
	//perform delete action
	if err := kubeapi.Delete(context.TODO(), label+"-web", metav1.DeleteOptions{
		PropagationPolicy: &deletePolicy,
	}); err != nil {
		panic(err)
	}
	fmt.Println("Deleted deployment")
}

func createPod(clientset *kubernetes.Clientset, ns, label string) {
	//create API connection
	kubeapi := clientset.CoreV1()

	//create Pod Spec
	pod := &apiv1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name: label + "-pod",
		},
		Spec: apiv1.PodSpec{
			Containers: []apiv1.Container{
				{
					Name:  label + "-pod",
					Image: "nginx:1.12",
					Ports: []apiv1.ContainerPort{
						{
							Name:          "http",
							Protocol:      apiv1.ProtocolTCP,
							ContainerPort: 80,
						},
					},
				},
			},
		},
	}
	fmt.Println("Creating Pod...")
	result, err := kubeapi.Pods(ns).Create(context.TODO(), pod, metav1.CreateOptions{})
	if err != nil {
		panic(err)
	}
	fmt.Printf("Created Pod %q\n", result.GetObjectMeta().GetName())
}

func deletePod(clientset *kubernetes.Clientset, ns, label string) {
	//create API connection
	kubeapi := clientset.CoreV1()
	//set delete policy
	deletePolicy := metav1.DeletePropagationForeground
	//perform delete action
	if err := kubeapi.Pods(ns).Delete(context.TODO(), label+"-pod", metav1.DeleteOptions{
		PropagationPolicy: &deletePolicy,
	}); err != nil {
		panic(err)
	}
	fmt.Println("Deleted pod")
}

func int32Ptr(i int32) *int32 { return &i }
