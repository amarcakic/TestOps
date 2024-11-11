# Selenium Test System Overview

This repository contains a system for running automated Selenium tests in a Kubernetes environment. The system consists of two main components:

- **Test Controller Pod**: Collects and sends test cases to the **Chrome Node Pod** for execution.
- **Chrome Node Pod**: Runs the Selenium tests in a headless Chrome browser environment.

## System Overview

### 1. **Test Controller Pod**
The Test Controller Pod is responsible for collecting and triggering the test cases defined in the Selenium scripts.

- The pod fetches the test cases and sends them to the **Chrome Node Pod** via a `ClusterIP` service (exposed on port 4444).
- The test controller runs a web server on port 8080 and connects to the Selenium Grid's **Chrome Node Pod** to run the tests.

### 2. **Chrome Node Pod**
The Chrome Node Pod runs a headless Chrome browser and executes the Selenium tests sent by the **Test Controller Pod**.

- It is configured as a Selenium Node connected to the **Selenium Hub** (managed by the Test Controller).
- The node listens on port 4444 for incoming test requests.

### 3. **Inter-Pod Communication**
- **Communication between the Test Controller and the Chrome Node** happens via Kubernetes' internal DNS system. The Test Controller sends requests to the Chrome Node via the `chrome-node-service`, which forwards traffic to the corresponding pod.
- The service `chrome-node-service` maps port 8080 from the **Test Controller** to port 4444 on the **Chrome Node**.

---

## How the Test Controller Pod Collects and Sends Tests to the Chrome Node Pod

1. The **Test Controller Pod** is deployed with an environment variable (`CHROME_NODE_URL`) that points to the **Chrome Node Pod's** service (`chrome-node-service`).
2. The Test Controller triggers test cases defined in the Selenium test scripts. These test cases are executed on the **Chrome Node Pod** via the Selenium WebDriver API.
3. The Test Controller continuously monitors the **Chrome Node Pod** and collects test results after execution.

---

## Steps to Deploy the System to Kubernetes

### A. **Deploy Locally (Minikube, Docker Desktop, etc.)**

1. **Set Up Kubernetes Cluster**:
   - Ensure you have Kubernetes running locally (using [Minikube](https://minikube.sigs.k8s.io/docs/) or [Docker Desktop](https://www.docker.com/products/docker-desktop)).
   - Verify the installation with `kubectl version`.

2. **Create Kubernetes Resources**:
   - Create Kubernetes deployment and service files for the Test Controller and Chrome Node.
   - Apply the deployments using the following command:
     ```bash
     kubectl apply -f k8s/chrome-node-deployment.yaml
     kubectl apply -f k8s/test-controller-deployment.yaml
     ```

3. **Verify Pods**:
   - Check if the pods are running correctly with:
     ```bash
     kubectl get pods
     ```

4. **Access Logs** (Optional):
   - To check the execution of your tests, view the logs of both the Test Controller and Chrome Node:
     ```bash
     kubectl logs -l app=test-controller
     kubectl logs -l app=chrome-node
     ```

---

### B. **Deploy to AWS EKS**

1. **Set Up AWS EKS Cluster**:
   - Set up your AWS EKS cluster by following the [EKS Getting Started Guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html).
   - Ensure that you have AWS CLI and `kubectl` configured with proper permissions.

2. **Deploy Kubernetes Resources to EKS**:
   - Once your EKS cluster is set up, use `kubectl` to apply the YAML files:
     ```bash
     kubectl apply -f k8s/chrome-node-deployment.yaml
     kubectl apply -f k8s/test-controller-deployment.yaml
     ```

3. **Verify Pods**:
   - Ensure that your pods are running by checking:
     ```bash
     kubectl get pods
     ```

4. **Service Communication**:
   - The services will be accessible within the EKS cluster, and the Test Controller Pod will be able to communicate with the Chrome Node Pod through the internal `chrome-node-service`.

---

## Inter-Pod Communication

1. **Kubernetes Service**:
   - The **Test Controller Pod** communicates with the **Chrome Node Pod** through the `chrome-node-service` service.
   - The service is defined with a `ClusterIP` type, which makes it accessible only within the Kubernetes cluster. This ensures that only the Test Controller can reach the Chrome Node.

2. **DNS Resolution**:
   - Kubernetes automatically handles DNS resolution within the cluster. The Test Controller Pod uses the service name (`chrome-node-service`) to resolve the IP address of the **Chrome Node Pod**.

3. **Ports**:
   - The Test Controller sends test execution requests to port 4444 on the Chrome Node Pod (which listens on port 4444) via the `chrome-node-service`.

---

## Conclusion

This system allows you to run Selenium tests in a distributed environment on Kubernetes, with a Test Controller Pod and a Chrome Node Pod communicating seamlessly. Whether you're deploying locally using Minikube or Docker Desktop, or deploying to AWS EKS, the system ensures that your Selenium tests are automatically triggered and executed.

For more information on how the deployments are configured and how the system works, refer to the `k8s/` folder in the project for the relevant YAML files.
