import os
import logging
from kubernetes import client, config

logger = logging.getLogger(__name__)

def load_k8s_config():
    """
    Loads Kubernetes configuration with the following priority:
    1. KUBECONFIG environment variable (OS level)
    2. In-cluster configuration (ServiceAccount)
    3. Default kubeconfig file (~/.kube/config)
    """
    
    # 1. Check KUBECONFIG environment variable
    kubeconfig_env = os.environ.get('KUBECONFIG')
    if kubeconfig_env and os.path.exists(kubeconfig_env):
        try:
            config.load_kube_config(config_file=kubeconfig_env)
            logger.info(f"Loaded Kubernetes configuration from KUBECONFIG env: {kubeconfig_env}")
            return True
        except Exception as e:
            logger.error(f"Failed to load config from KUBECONFIG={kubeconfig_env}: {e}")

    # 2. Try in-cluster configuration
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes configuration")
        return True
    except config.ConfigException:
        logger.debug("In-cluster configuration not found")
    except Exception as e:
        logger.error(f"Error loading in-cluster config: {e}")

    # 3. Fallback to default kubeconfig
    try:
        config.load_kube_config()
        logger.info("Loaded default Kubernetes configuration (~/.kube/config)")
        return True
    except Exception as e:
        logger.error(f"Failed to load default kubeconfig: {e}")
        
    return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if load_k8s_config():
        v1 = client.CoreV1Api()
        print("Successfully connected to Kubernetes!")
        # Example: list nodes to verify connectivity
        try:
            nodes = v1.list_node()
            print(f"Cluster has {len(nodes.items)} nodes.")
        except Exception as e:
            print(f"Could not list nodes: {e}")
    else:
        print("Failed to initialize Kubernetes client.")
