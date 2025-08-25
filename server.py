from mcp.server.fastmcp import FastMCP
from kubernetes import config, client
from kubernetes.client import (
    V1Pod, V1ObjectMeta, V1PodSpec, V1Container,
    V1Namespace, V1Service, V1ServiceSpec, V1ServicePort
)

# Load kubeconfig
config.load_kube_config()

core = client.CoreV1Api()
apps = client.AppsV1Api()

mcp = FastMCP("k8s-mcp")

# -----------------------
# Helper: Ensure Namespace Exists
# -----------------------
def ensure_namespace_exists(name: str) -> str:
    try:
        core.read_namespace(name)
        return f"Namespace '{name}' already exists."
    except client.exceptions.ApiException as e:
        if e.status == 404:
            ns = V1Namespace(metadata=V1ObjectMeta(name=name))
            core.create_namespace(body=ns)
            return f"✅ Namespace '{name}' created."
        else:
            raise


# -----------------------
# Tool: Create a Pod
# -----------------------
@mcp.tool("create_pod")
def create_pod(name: str, namespace: str = "default", image: str = "nginx") -> str:
    try:
        ns_msg = ensure_namespace_exists(namespace)

        pod = V1Pod(
            metadata=V1ObjectMeta(
                name=name,
                labels={"app": name}  # label so service selectors can find it
            ),
            spec=V1PodSpec(
                containers=[V1Container(name="main", image=image)]
            )
        )
        core.create_namespaced_pod(namespace=namespace, body=pod)
        return f"{ns_msg}\n✅ Pod '{name}' created in namespace '{namespace}' with image '{image}'."
    except client.exceptions.ApiException as e:
        return f"❌ Failed to create pod: {e}"


# -----------------------
# Tool: Delete a Pod
# -----------------------
@mcp.tool("delete_pod")
def delete_pod(name: str, namespace: str = "default") -> str:
    try:
        core.delete_namespaced_pod(name=name, namespace=namespace)
        return f"🗑️ Pod '{name}' deleted from namespace '{namespace}'."
    except client.exceptions.ApiException as e:
        return f"❌ Failed to delete pod: {e}"


# -----------------------
# Tool: Create Namespace
# -----------------------
@mcp.tool("create_namespace")
def create_namespace(name: str) -> str:
    try:
        ns = V1Namespace(metadata=V1ObjectMeta(name=name))
        core.create_namespace(body=ns)
        return f"✅ Namespace '{name}' created successfully."
    except client.exceptions.ApiException as e:
        return f"❌ Failed to create namespace: {e}"


# -----------------------
# Tool: Create a Service
# -----------------------
@mcp.tool("create_service")
def create_service(
    name: str,
    namespace: str = "default",
    port: int = 80,
    target_port: int = 80,
    service_type: str = "ClusterIP",
    selector_key: str = "app",
    selector_value: str = None
) -> str:
    try:
        ns_msg = ensure_namespace_exists(namespace)

        if not selector_value:
            selector_value = name

        service = V1Service(
            metadata=V1ObjectMeta(name=name),
            spec=V1ServiceSpec(
                type=service_type,
                selector={selector_key: selector_value},
                ports=[V1ServicePort(port=port, target_port=target_port)]
            )
        )
        core.create_namespaced_service(namespace=namespace, body=service)
        return f"{ns_msg}\n✅ Service '{name}' created in namespace '{namespace}' of type '{service_type}' exposing port {port}->{target_port}."
    except client.exceptions.ApiException as e:
        return f"❌ Failed to create service: {e}"


# -----------------------
# Tool: Describe a Pod (with Events)
# -----------------------
@mcp.tool("describe_pod")
def describe_pod(name: str, namespace: str = "default") -> str:
    try:
        pod = core.read_namespaced_pod(name=name, namespace=namespace)
        desc_lines = [
            f"Name:        {pod.metadata.name}",
            f"Namespace:   {pod.metadata.namespace}",
            f"Node:        {pod.spec.node_name}",
            f"Labels:      {pod.metadata.labels}",
            f"Annotations: {pod.metadata.annotations}",
            f"Status:      {pod.status.phase}",
            f"IP:          {pod.status.pod_ip}",
            "Containers:"
        ]
        for c in pod.spec.containers:
            cs = next((s for s in (pod.status.container_statuses or []) if s.name == c.name), None)
            desc_lines.append(
                f"  - Name: {c.name}, Image: {c.image}, Ready: {cs.ready if cs else 'N/A'}, RestartCount: {cs.restart_count if cs else 0}"
            )
        desc_lines.append("\nEvents:")
        desc_lines.append("Events functionality is not implemented.")
        return "\n".join([str(l) for l in desc_lines])
    except client.exceptions.ApiException as e:
        return f"❌ Failed to describe pod: {e}"




# -----------------------
# Tool: Describe a Pod (with Events)
# -----------------------
@mcp.tool("describe_pod")
def describe_pod(name: str, namespace: str = "default") -> str:
    try:
        pod = core.read_namespaced_pod(name=name, namespace=namespace)
        desc_lines = [
            f"Name:        {pod.metadata.name}",
            f"Namespace:   {pod.metadata.namespace}",
            f"Node:        {pod.spec.node_name}",
            f"Labels:      {pod.metadata.labels}",
            f"Annotations: {pod.metadata.annotations}",
            f"Status:      {pod.status.phase}",
            f"IP:          {pod.status.pod_ip}",
            "Containers:"
        ]
        for c in pod.spec.containers:
            cs = next((s for s in (pod.status.container_statuses or []) if s.name == c.name), None)
            desc_lines.append(
                f"  - Name: {c.name}, Image: {c.image}, Ready: {cs.ready if cs else 'N/A'}, RestartCount: {cs.restart_count if cs else 0}"
            )
        desc_lines.append("\nEvents:")
        desc_lines.append("Events functionality is not implemented.")
        return "\n".join([str(l) for l in desc_lines])
    except client.exceptions.ApiException as e:
        return f"❌ Failed to describe pod: {e}"




# -----------------------
# Tool: Get Pod Logs
# -----------------------
@mcp.tool("get_pod_logs")
def get_pod_logs(name: str, namespace: str = "default", container: str = None) -> str:
    """
    Get logs from a Kubernetes Pod (like `kubectl logs`).
    """
    try:
        logs = core.read_namespaced_pod_log(name=name, namespace=namespace, container=container)
        return f"📜 Logs for Pod '{name}' (namespace: {namespace}):\n\n{logs}"
    except client.exceptions.ApiException as e:
        return f"❌ Failed to get pod logs: {e}"


if __name__ == "__main__":
    mcp.run()
