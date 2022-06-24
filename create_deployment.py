import configparser
import yaml

from kubernetes import client

# def create_sorterd_pod():
#     config = configparser.ConfigParser()
#     with open("config.cfg") as cfg:
#         config.read_file(cfg)
#     input_dir = config.get("reader", "image_folder")
#     return client.V1Pod(
#         api_version = "v1",
#         kind = "Pod",
#         metadata = client.V1ObjectMeta(
#             name = "sorterd",
#         ),
#         spec = client.V1PodSpec(
#             volumes = [
#                 client.V1PersistentVolume(
#                     metadata = client.V1ObjectMeta(
#                         name = "reader-volume"
#                     ),
#                     spec = client.V1PersistentVolumeSpec(
#                         host_path = input_dir,
#                         access_modes = ["ReadOnlyMany"]
#                     )
#                 )],
#             containers = [
#                 client.V1Container(
#                     name = "sorterd",
#                     image = "color-grouper-image",
#                     resources = client.V1ResourceRequirements(
#                         {
#                             "memory": "128Mi",
#                             "cpu": "500m"
#                         }
#                     ),
#                     command = ["sorterd"],
#                     volume_mounts = [
#                         client.V1VolumeMount(
#                             name = "target_dir",
#                             mount_path = "/output_folder/"
#                         )
#                     ]         
#                 )
#             ],
#         )
#     )

def create_pod(name, image):
    return client.V1Pod(
        api_version = "v1",
        kind = "Pod",
        metadata = {
            "name": name,
        },
        spec = {
            "containers" : [
                {
                    "name" : name,
                    "image" : image,
                    "imagePullPolicy": "Never",
                    "resources" : {
                        "limits": {
                            "memory": "128M",
                            "cpu": "500m"
                        }
                    },
                    "command" : [name],                    
                }
            ],
        }
    )


def main():
    config = configparser.ConfigParser()
    with open("config.cfg") as cfg:
        config.read_file(cfg)
    input_dir = config.get("reader", "image_folder")
    target_dir = config.get("sorter", "target_dir")
    image_name = config.get("main", "docker_image_name")
    pods = []
    pvolumes = []
    pv_claims = []
    for app in ["reader", "generator", "sorter"]:
        pod = create_pod(app, image_name)
        # mount volumes for some containers
        if app == "reader":
            pv = client.V1PersistentVolume(
                    api_version = "v1",
                    kind = "PersistentVolume",
                    metadata = client.V1ObjectMeta(
                        name = "reader-pv-volume"
                    ),
                    spec = client.V1PersistentVolumeSpec(
                        capacity = {"storage": "100M"},
                        host_path = {"path": input_dir},
                        access_modes = ["ReadOnlyMany"]
                    )
                 )
            pv_claim =  \
                client.V1PersistentVolumeClaim(
                    api_version = "v1",
                    kind = "PersistentVolumeClaim",
                    metadata=client.V1ObjectMeta(name="reader-pv-claim"),
                    spec = client.V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources = client.V1ResourceRequirements(requests={"storage": "100M"}),
                        volume_name = pv.metadata.name
                    )
                )
            pvolumes.append(pv)
            pv_claims.append(pv_claim)
            pod.spec["volumes"] = [
                client.V1Volume(
                    name = "reader-volume",
                    persistent_volume_claim = 
                        client.V1PersistentVolumeClaimVolumeSource(
                                claim_name = pv_claim.metadata.name
                        ) 
                    
                )
            ]
            pod.spec["containers"][0]["volumeMounts"] = [
                {
                    "name" : "reader-volume",
                    "readOnly" : True,
                    "mountPath" : "/image_folder/"
                }
            ]
        elif app == "sorter":
            pv = client.V1PersistentVolume(
                    api_version = "v1",
                    kind = "PersistentVolume",
                    metadata = client.V1ObjectMeta(
                        name = "target-dir-pv"
                    ),
                    spec = client.V1PersistentVolumeSpec(
                        capacity = {"storage": "100M"},
                        host_path = {"path": target_dir},
                        access_modes = ["ReadOnlyMany"]
                    )
                 )
            pv_claim =  \
                client.V1PersistentVolumeClaim(
                    api_version = "v1",
                    kind = "PersistentVolumeClaim",
                    metadata=client.V1ObjectMeta(name="sorter-pv-claim"),
                    spec = client.V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources = client.V1ResourceRequirements(requests={"storage": "100M"}),
                        volume_name = pv.metadata.name
                    )
                )
            pvolumes.append(pv)
            pv_claims.append(pv_claim)
            pod.spec["volumes"] = [
                client.V1Volume(
                    name = "target-dir",
                    persistent_volume_claim = 
                        client.V1PersistentVolumeClaimVolumeSource(
                            claim_name = pv_claim.metadata.name
                        ) 
                )
            ]
            pod.spec["containers"][0]["volumeMounts"] = [
                {
                    "name" : "target-dir",
                    "mountPath" : "/output_folder/"
                }
            ]
        pods.append(pod)

    with open("./kube.yaml", "w") as file:
        yaml.dump_all(client.ApiClient().sanitize_for_serialization(pvolumes + pv_claims + pods), stream=file)
        # print(yaml.dump(client.ApiClient().sanitize_for_serialization(pvolumes + pv_claims + pods)), file=file)
        # print(json.dumps(client.ApiClient().sanitize_for_serialization(pvolumes + pv_claims + pods)), file=file)
        # print(json.dumps(client.ApiClient().sanitize_for_serialization(pv_claims)), file=file)
        # print(json.dumps(client.ApiClient().sanitize_for_serialization(pods)), file=file)

if __name__ == '__main__':
    main()
