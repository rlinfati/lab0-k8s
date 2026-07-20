# jupyterhub_config.py
import sys
import os
import socket

c = get_config()

from oauthenticator.azuread import AzureAdOAuthenticator
class AzureMenosCeroOAuth(AzureAdOAuthenticator):
    def normalize_username(self, username):
        return username.split("@")[0].lower()

c.JupyterHub.hub_bind_url = "http://" + socket.gethostbyname( socket.gethostname() ) + ":8001"
c.JupyterHub.hub_connect_url = "http://api.jupyterhub.svc.cluster.local:8001"
# c.JupyterHub.authenticator_class = "shared-password"
# c.JupyterHub.authenticator_class = "azuread"
# c.JupyterHub.authenticator_class = AzureMenosCeroOAuth
c.JupyterHub.authenticator_class = AzureMenosCeroOAuth
c.JupyterHub.spawner_class = "kubespawner.KubeSpawner"
c.KubeSpawner.image_pull_policy = "IfNotPresent"
c.JupyterHub.shutdown_on_logout = True
c.JupyterHub.db_url = "sqlite:////etc/jupyterhub/database/jupyterhub.sqlite"
c.JupyterHub.allow_named_servers = True

c.Authenticator.admin_users = {u.lower() for u in open("/etc/jupyterhub/secrets/AdminUsers").read().split()}
c.Authenticator.allow_all = True
c.OAuthenticator.oauth_callback_url = open("/etc/jupyterhub/secrets/OAuthCallBack").read().strip()
c.OAuthenticator.client_id = open("/etc/jupyterhub/secrets/ClientID").read().strip()
c.OAuthenticator.client_secret = open("/etc/jupyterhub/secrets/SecretID").read().strip()
c.AzureAdOAuthenticator.tenant_id = open("/etc/jupyterhub/secrets/TenantID").read().strip()
c.AzureAdOAuthenticator.username_claim = "unique_name"
c.SharedPasswordAuthenticator.user_password  = "1d74ebcc-9e31-478e-8a5a-2352fec496e6"
c.SharedPasswordAuthenticator.admin_password = "2f60f092-cb7e-4f63-b6e9-a2973d061acf"

c.KubeSpawner.storage_pvc_ensure = True
c.KubeSpawner.delete_pvc = False
c.KubeSpawner.storage_class = "localpath"
c.KubeSpawner.pvc_name_template = "{username}"
c.KubeSpawner.storage_capacity = "8Gi"

c.KubeSpawner.volume_mounts = [
    {
        "name": "work-{username}",
        "mountPath": "/home/jovyan/work",
    },
    {
        "name": "gurobi",
        "mountPath": "/opt/gurobi/gurobi.lic",
        "subPath": "gurobi.lic",
    },
]
c.KubeSpawner.volumes = [
    {
        "name": "work-{username}",
        "persistentVolumeClaim": {"claimName": "{username}"},
    },
    {
        "name": "gurobi",
        "secret": {"secretName": "gurobi"},
    },
]

c.KubeSpawner.extra_container_config = { "envFrom": [ { "secretRef": { "name": "ampl" } } ] }

IMAGEallowed = (
    "ghcr.io/rlinfati/",
    "quay.io/jupyter/",
)

OSname = next(
    (l.split("=", 1)[1].strip().strip('"')
    for l in open("/etc/os-release")
    if l.startswith("PRETTY_NAME=")),
    os.uname().sysname + " " + os.uname().release
)
UNAMEstr = os.uname().sysname + " " + os.uname().release

CPUname = next(
    (line.split(":", 1)[1].strip()
    for line in open("/proc/cpuinfo")
    if line.startswith("model name")),
    os.uname().machine
)
CPUtotal  = os.cpu_count() or 0

MEMtotal  = next(int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemTotal")) // 1024 // 1024

hasNVIDIA = (os.path.exists("/proc/driver/nvidia/version") or os.path.exists("/sys/module/nvidia/version"))
def getNVIDIA():
    base = "/proc/driver/nvidia/gpus"
    gpus = []
    try:
        for gpu in sorted(os.listdir(base)):
            info = os.path.join(base, gpu, "information")
            with open(info) as f:
                for line in f:
                    if line.startswith("Model:"):
                        gpus.append(line.split(":", 1)[1].strip())
                        break
    except Exception:
            pass
    if not gpus:
        return "No NVIDIA GPU detected"
    unique = sorted(set(gpus))
    if len(unique) == 1:
        return f"{len(gpus)} × {unique[0]}"
    return ", ".join(unique)
getNVIDIA = getNVIDIA()
def numNVIDIA():
    base = "/proc/driver/nvidia/gpus"
    gpus = []
    try:
        for gpu in sorted(os.listdir(base)):
            info = os.path.join(base, gpu, "information")
            with open(info) as f:
                for line in f:
                    if line.startswith("Model:"):
                        gpus.append(line.split(":", 1)[1].strip())
                        break
    except Exception:
            pass
    return len(gpus)
numNVIDIA = numNVIDIA()

spawner_image_lab0 = """
    <optgroup label="rlinfati/lab0">
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-julia-1.13">          Julia 1.13 alpha/beta/rc</option>
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-julia-1.12" selected> Julia 1.12 stable</option>
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-julia-1.10">          Julia 1.10 LTS</option>
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-anaconda-latest">     Anaconda</option>
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-devcpp-latest">       devcpp</option>
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-base-latest">         base</option>
    </optgroup>
"""
spawner_image_jupyter = """
    <optgroup label="jupyter/notebook">
    <option value="quay.io/jupyter/julia-notebook:latest">                           Julia</option>
    <option value="quay.io/jupyter/scipy-notebook:latest">                           SciPy</option>
    <option value="quay.io/jupyter/r-notebook:latest">                               R</option>
    <option value="quay.io/jupyter/pytorch-notebook:latest">                         PyTorch</option>
    <option value="quay.io/jupyter/tensorflow-notebook:latest">                      TensorFlow</option>
    </optgroup>
"""

spawner_image_cuda = """
    <optgroup label="NVIDIA/CUDA">
    <option value="ghcr.io/rlinfati/lab0-container:jupyter-lab-juliacuda-1.10">      [lab0]    Julia 1.10 + cuda</option>
    <option value="quay.io/jupyter/pytorch-notebook:cuda13-latest">                  [jupyter] PyTorch    + cuda</option>
    <option value="quay.io/jupyter/tensorflow-notebook:cuda-latest">                 [jupyter] TensorFlow + cuda</option>
    </optgroup>
""" if hasNVIDIA else ""

def spawner_cpu():
    values = [1, 2] + list(range(4, CPUtotal//2 + 1, 4))
    return "\n".join(
        f'<option value="{i}">{i} CPU</option>'
        for i in values
    )
spawner_cpu = spawner_cpu()

def spawner_mem():
    values = list(range(4, min(MEMtotal, 16) + 1, 4))
    if MEMtotal > 16:
        values += list(range(24, MEMtotal + 1, 8))
    return "\n".join(
        f'<option value="{i}G">{i} GB</option>'
        for i in values
    )
spawner_mem = spawner_mem()

def spawner_gpu():
    values = list(range(0, numNVIDIA + 1, 1))
    return "\n".join(
        f'<option value="{i}">{i} GPU</option>'
        for i in values
    )
spawner_gpu = spawner_gpu()

c.KubeSpawner.options_form = f"""

    <table class="table table-condensed"><tbody>
        <tr><th style="width:120px;">OS</th>    <td>{OSname}</td></tr>
        <tr><th>Kernel</th>                     <td>{UNAMEstr}</td></tr>
        <tr><th>CPU</th>                        <td>{CPUtotal} × {CPUname}</td></tr>
        <tr><th>Memory</th>                     <td>{((MEMtotal + 7) // 8) * 8} GB total, {MEMtotal} GB usable</td></tr>
        <tr><th>NVIDIA</th>                     <td>{getNVIDIA}</td></tr>
    </tbody></table>

    <div class="form-group" style="display:flex; align-items:center; gap:10px;">
        <label for="image" class="control-label" style="width:120px; text-align:right;">Image</label>
        <select name="image" class="form-control">
            {spawner_image_lab0}
            {spawner_image_jupyter}
            {spawner_image_cuda}
        </select>
    </div>
    <div class="form-group" style="display:flex; align-items:center; gap:10px;">
        <label for="cpu" class="control-label" style="width:120px; text-align:right;">CPU</label>
        <select name="cpu" class="form-control">
            {spawner_cpu}
        </select>
    </div>
    <div class="form-group" style="display:flex; align-items:center; gap:10px;">
        <label for="mem" class="control-label" style="width:120px; text-align:right;">Memory</label>
        <select name="mem" class="form-control">
            {spawner_mem}
        </select>
    </div>
    <div class="form-group" style="display:flex; align-items:center; gap:10px;">
        <label for="gpu" class="control-label" style="width:120px; text-align:right;">GPU</label>
        <select name="gpu" class="form-control">
            {spawner_gpu}
        </select>
    </div>
"""

def options_from_form(formdata):
    image =     formdata.get("image", ["ghcr.io/rlinfati/lab0-container:jupyter-lab-base-latest"])[0]
    cpu   = int(formdata.get("cpu", ["1"])[0])
    mem   =     formdata.get("mem", ["2G"])[0]
    gpu   = int(formdata.get("gpu", ["0"])[0])

    if not image.startswith(IMAGEallowed):
        raise ValueError(f"Image '{image}' is not allowed")

    if cpu > CPUtotal:
        raise ValueError(f"Requested CPU ({cpu}) exceeds available CPU ({CPUtotal}).")

    if mem[:-1].isdigit():
        mem_value = int(mem[:-1])
        if mem.endswith("G") and mem_value > MEMtotal:
            raise ValueError(f"Requested MEM ({mem}) exceeds available MEM ({MEMtotal}G).")
    else:
        raise ValueError(f"Invalid memory format: {mem}")

    if gpu > 0 and not hasNVIDIA:
        raise ValueError("GPU not available.")

    return {
        "image": image,
        "cpu":   cpu,
        "mem":   mem,
        "gpu":   gpu,
    }
c.KubeSpawner.options_from_form = options_from_form

def apply_user_options(spawner, options):
    spawner.image = options["image"]
    spawner.cpu_guarantee = options["cpu"]
    spawner.cpu_limit = options["cpu"]
    spawner.mem_guarantee = options["mem"]
    spawner.mem_limit = options["mem"]

    if options["gpu"] > 0:
        spawner.extra_resource_limits = spawner.extra_resource_limits or {}
        spawner.extra_resource_limits["nvidia.com/gpu"] = options["gpu"]

c.KubeSpawner.apply_user_options = apply_user_options

c.JupyterHub.services = [ { "name": "jupyterhub-idle-culler-service",
                            "command": [sys.executable, "-m", "jupyterhub_idle_culler", "--timeout=7200"],
                            "admin": True } ]

# eof