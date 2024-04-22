from kubernetes import client, config
from flask import Flask, request
import random, string, json
import json

# Load Kubernetes config
config.load_kube_config()

# Create Kubernetes API clients
batch_v1 = client.BatchV1Api()
core_v1 = client.CoreV1Api()

app = Flask(__name__)

@app.route('/config', methods=['GET'])
def get_config():
    pods = []

    # Get all pods across all namespaces
    ret = core_v1.list_pod_for_all_namespaces(watch=False)

    # Extract required fields from the Pod object
    for pod in ret.items:
        pod_info = {
            "node": pod.spec.node_name,
            "ip": pod.status.pod_ip,
            "namespace": pod.metadata.namespace,
            "name": pod.metadata.name,
            "status": pod.status.phase
        }
        pods.append(pod_info)

    output = {"pods": pods}
    output = json.dumps(output)

    return output

@app.route('/img-classification/free', methods=['POST'])
def post_free():

    # Parse the request body
    content_type = request.content_type
    if content_type == 'application/json':
        data = request.get_json()
    else:
        data = json.loads(request.data.decode('utf-8'))
    dataset = data['dataset']

    # Create the job
    job_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    container_name = 'free-classifier-container'
    image_name = 'jjyyjay/classifier-image'
    env_vars = [
        client.V1EnvVar(name='DATASET', value=dataset),
        client.V1EnvVar(name='TYPE', value='ff')
    ]
    container = client.V1Container(
        name=container_name,
        image=image_name,
        env=env_vars
    )
    spec = client.V1PodSpec(
        restart_policy='OnFailure',
        containers=[container]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': 'free-classification'}),
        spec=spec
    )
    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(template=template)
    )
    batch_v1.create_namespaced_job(
        namespace='free-service',
        body=job
    )

    return "success"

@app.route('/img-classification/premium', methods=['POST'])
def post_premium():

    # Parse the request body
    content_type = request.content_type
    if content_type == 'application/json':
        data = request.get_json()
    else:
        data = json.loads(request.data.decode('utf-8'))
    dataset = data['dataset']

    # Create the job
    job_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    container_name = 'premium-classifier-container'
    image_name = 'jjyyjay/classifier-image'
    env_vars = [
        client.V1EnvVar(name='DATASET', value=dataset),
        client.V1EnvVar(name='TYPE', value='cnn')
    ]
    container = client.V1Container(
        name=container_name,
        image=image_name,
        env=env_vars
    )
    spec = client.V1PodSpec(
        restart_policy='OnFailure',
        containers=[container]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': 'premium-classification'}),
        spec=spec
    )
    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(template=template)
    )
    batch_v1.create_namespaced_job(
        namespace='default',
        body=job
    )

    return "success"

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)