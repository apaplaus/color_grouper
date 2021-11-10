import configparser
import json

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

def create_pod(name):
    return client.V1Pod(
        api_version = "v1",
        kind = "Pod",
        metadata = client.V1ObjectMeta(
            name = name,
        ),
        spec = client.V1PodSpec(
            containers = [
                client.V1Container(
                    name = name,
                    image = "color-grouper-image",
                    resources = client.V1ResourceRequirements(
                        {
                            "memory": "128Mi",
                            "cpu": "500m"
                        }
                    ),
                    command = [name],                    
                )
            ],
        )
    )


def main():
    config = configparser.ConfigParser()
    with open("config.cfg") as cfg:
        config.read_file(cfg)
    input_dir = config.get("reader", "image_folder")
    target_dir = config.get("sorter", "target_dir")
    pods = []
    pvolumes = []
    pv_claims = []
    for app in ["reader", "generator", "sorter"]:
        pod = create_pod(app)
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
            pod.spec.volumes = [
                client.V1Volume(
                    name = "reader-volume",
                    persistent_volume_claim = 
                        client.V1PersistentVolumeClaimVolumeSource(
                                claim_name = pv_claim.metadata.name
                        ) 
                    
                )
            ]
            pod.spec.containers[0].volume_mounts = [
                client.V1VolumeMount(
                    name = "reader-volume",
                    read_only = True,
                    mount_path = "/image_folder/"
                )
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
            pod.spec.volumes = [
                client.V1Volume(
                    name = "target-dir",
                    persistent_volume_claim = 
                        client.V1PersistentVolumeClaimVolumeSource(
                            claim_name = pv_claim.metadata.name
                        ) 
                )
            ]
            pod.spec.containers[0].volume_mounts = [
                client.V1VolumeMount(
                    name = "target-dir",
                    read_only = True,
                    mount_path = "/output_folder/"
            )]
        pods.append(pod)

    with open("./kube.yml", "w") as file:
        for pv in pvolumes:
            print(json.dumps(client.ApiClient().sanitize_for_serialization(pv)), file=file)
        for pv_claim in pv_claims:
            print(json.dumps(client.ApiClient().sanitize_for_serialization(pv_claim)), file=file)
        for pod in pods:
            print(json.dumps(client.ApiClient().sanitize_for_serialization(pod)), file=file)

if __name__ == '__main__':
    main()
