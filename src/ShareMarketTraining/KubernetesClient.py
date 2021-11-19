from kubernetes import client, config
import base64, json

class KubernetesClient():

    def __init__(self):
        config.load_incluster_config()
        self.v1 = client.CoreV1Api()

    def getFirebaseSA(self):
        secret_encoded = self.v1.read_namespaced_secret("firebase-sa","saikrishnaa97")
        secret1 = base64.b64decode(secret_encoded.data['sa.txt'])
        secret_decoded = base64.b64decode(secret1).decode('utf-8')
        secret_decoded = secret_decoded.replace('\n', '')
        f = open("/opt/ShareMarketTraining/rest_client/fbSA.json","a")
        f.write(secret_decoded)
        f.close()