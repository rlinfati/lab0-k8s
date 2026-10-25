# jupyterhub_config.py
import html
import json
import socket
import sys

import kubernetes
from oauthenticator.azuread import AzureAdOAuthenticator

c = get_config()

# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------

class AzureMenosCeroOAuth(AzureAdOAuthenticator):
    def normalize_username(self, username):
        return username.partition("@")[0].lower()

def read_secret(name):
    path = f"/etc/jupyterhub/secrets/{name}"
    with open(path, encoding="utf-8") as file:
        return file.read().strip()

c.Authenticator.admin_users = {
    username.lower()
    for username in read_secret("AdminUsers").split()
}
c.Authenticator.allow_all = True

auth_mode = read_secret("AuthMode")
if auth_mode == "AzureMenosCeroOAuth":
    c.JupyterHub.authenticator_class = AzureMenosCeroOAuth

    c.OAuthenticator.oauth_callback_url = read_secret("OAuthCallBack")
    c.OAuthenticator.client_id = read_secret("ClientID")
    c.OAuthenticator.client_secret = read_secret("SecretID")

    c.AzureAdOAuthenticator.tenant_id = read_secret("TenantID")
    c.AzureAdOAuthenticator.username_claim = "unique_name"
elif auth_mode == "shared-password":
    c.JupyterHub.authenticator_class = "shared-password"

    c.SharedPasswordAuthenticator.user_password = read_secret("SharedPassUsr")
    c.SharedPasswordAuthenticator.admin_password = read_secret("SharedPassAdm")
else:
    raise ValueError(f"Invalid AuthMode: {auth_mode}")

# -----------------------------------------------------------------------------
# JupyterHub
# -----------------------------------------------------------------------------

hub_ip = socket.gethostbyname(socket.gethostname())

c.JupyterHub.hub_bind_url = f"http://{hub_ip}:8001"
c.JupyterHub.hub_connect_url = "http://api.jupyterhub.svc.cluster.local:8001"
c.JupyterHub.spawner_class = "kubespawner.KubeSpawner"

c.JupyterHub.shutdown_on_logout = True
c.JupyterHub.db_url = (
    "sqlite:////etc/jupyterhub/database/jupyterhub.sqlite"
)
c.JupyterHub.upgrade_db = True
c.JupyterHub.allow_named_servers = True

# -----------------------------------------------------------------------------
# KubeSpawner defaults
# -----------------------------------------------------------------------------

c.KubeSpawner.image_pull_policy = "IfNotPresent"
c.KubeSpawner.priority_class_name = "jupyterlabs"

c.KubeSpawner.storage_pvc_ensure = True
c.KubeSpawner.delete_pvc = False
c.KubeSpawner.storage_class = "localpath"
c.KubeSpawner.remember_pvc_name = False
c.KubeSpawner.storage_capacity = "8Gi"

c.KubeSpawner.volumes = [
    {
        "name": "gurobi",
        "secret": {
            "secretName": "gurobi",
        },
    },
]

c.KubeSpawner.volume_mounts = [
    {
        "name": "gurobi",
        "mountPath": "/opt/gurobi/gurobi.lic",
        "subPath": "gurobi.lic",
        "readOnly": True,
    },
]

c.KubeSpawner.extra_container_config = {
    "envFrom": [
        {
            "secretRef": {
                "name": "ampl",
            },
        },
    ],
}

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

HOSTNAME_LABEL = "kubernetes.io/hostname"
CPU_MODEL_ANNOTATION = "cpu-model"
# kubectl annotate node $(hostname --long) cpu-model-
# kubectl annotate node $(hostname --long) cpu-model="CPU Model"
THREADS_PER_CORE_ANNOTATION = "threads-per-core"
# kubectl annotate node $(hostname --long) threads-per-core-
# kubectl annotate node $(hostname --long) threads-per-core=2
GPU_MODEL_ANNOTATION = "gpu-model"
# kubectl annotate node $(hostname --long) gpu-model-
# kubectl annotate node $(hostname --long) gpu-model="GPU Model"
JUPYTERLAB_LABELS = (
    ("m0net/run.jupyterlab", "true"),
    ("m0net/run.jupytermin", "true"),
)

MEMORY_SAFETY_MARGIN_GIB = 2
CPUFREE_MAX_CPU = 4

GPU_RESOURCES = (
    "nvidia.com/gpu",
    "amd.com/gpu",
    "gpu.intel.com/i915",
    "gpu.intel.com/xe",
)

ALLOWED_IMAGE_PREFIXES = (
    "ghcr.io/rlinfati/",
    "quay.io/jupyter/",
)

DEFAULT_IMAGE = (
    "ghcr.io/rlinfati/"
    "lab0-container:jupyter-lab-base-latest"
)

IMAGE_GROUPS = (
    (
        "rlinfati/lab0",
        (
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.14",
                "Julia 1.14 (pre-release)",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.13",
                "Julia 1.13 (stable, recommended)",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.12",
                "Julia 1.12 (oldstable)",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.10",
                "Julia 1.10 (LTS)",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-anaconda-latest",
                "Python (Anaconda)",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-devcpp-latest",
                "C/C++ (GCC, Clang)",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-base-latest",
                "Base (JupyterLab)",
            ),
        ),
    ),
    (
        "Jupyter Docker Stacks",
        (
            (
                "quay.io/jupyter/julia-notebook:latest",
                "Julia (latest)",
            ),
            (
                "quay.io/jupyter/scipy-notebook:latest",
                "Python (SciPy)",
            ),
            (
                "quay.io/jupyter/r-notebook:latest",
                "R (latest)",
            ),
            (
                "quay.io/jupyter/pytorch-notebook:latest",
                "Python (PyTorch)",
            ),
            (
                "quay.io/jupyter/tensorflow-notebook:latest",
                "Python (TensorFlow)",
            ),
        ),
    ),
)

CUDA_IMAGES = (
    (
        "ghcr.io/rlinfati/"
        "lab0-container:jupyter-lab-juliacuda-1.10",
        "Julia 1.10 (CUDA)",
    ),
    (
        "quay.io/jupyter/pytorch-notebook:cuda13-latest",
        "Python (PyTorch, CUDA)",
    ),
    (
        "quay.io/jupyter/tensorflow-notebook:cuda-latest",
        "Python (TensorFlow, CUDA)",
    ),
)

# -----------------------------------------------------------------------------
# Kubernetes inventory
# -----------------------------------------------------------------------------

def kubernetes_api():
    kubernetes.config.load_incluster_config()
    return kubernetes.client.CoreV1Api()

def cpu_quantity(value):
    value = str(value)

    for suffix, divisor in (("n", 1e9), ("u", 1e6), ("m", 1e3)):
        if value.endswith(suffix):
            return float(value[:-1]) / divisor

    return float(value)

def memory_quantity_gib(value):
    value = str(value)

    suffixes = {
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "K": 1000,
        "M": 1000**2,
        "G": 1000**3,
    }

    for suffix, multiplier in suffixes.items():
        if value.endswith(suffix):
            number = float(value[:-len(suffix)])
            return number * multiplier / 1024**3

    return float(value) / 1024**3

def threads_per_core(annotations):
    try:
        value = int(annotations.get(THREADS_PER_CORE_ANNOTATION, ""))
    except ValueError:
        return 1

    return value if value >= 1 else 1

def node_is_ready(node):
    return any(
        condition.type == "Ready"
        and condition.status == "True"
        for condition in node.status.conditions or []
    )

def node_hostname(node):
    labels = node.metadata.labels or {}
    return labels.get(HOSTNAME_LABEL, node.metadata.name)

def node_taints(node):
    return [
        {
            "key": taint.key,
            "value": taint.value or "",
            "effect": taint.effect or "",
        }
        for taint in node.spec.taints or []
    ]

def gpu_counts(quantities):
    counts = {}

    for resource in GPU_RESOURCES:
        count = int(quantities.get(resource, 0))

        if count > 0:
            counts[resource] = count

    return counts

def container_requests(container):
    resources = container.resources
    requests = (resources.requests if resources else None) or {}
    limits = (resources.limits if resources else None) or {}

    return {
        "cpu": cpu_quantity(requests.get("cpu", 0)),
        "memory": memory_quantity_gib(requests.get("memory", 0)),
        **{
            resource: int(
                requests.get(resource, limits.get(resource, 0))
            )
            for resource in GPU_RESOURCES
        },
    }

def pod_requests(pod):
    containers = [
        container_requests(container)
        for container in pod.spec.containers or []
    ]
    init_containers = [
        container_requests(container)
        for container in pod.spec.init_containers or []
    ]

    return {
        key: max(
            sum(container[key] for container in containers),
            max((init[key] for init in init_containers), default=0),
        )
        for key in ("cpu", "memory", *GPU_RESOURCES)
    }

def get_node_pod_load(api, pod_usage):
    try:
        pods = api.list_pod_for_all_namespaces(
            field_selector=(
                "status.phase!=Succeeded,status.phase!=Failed"
            ),
        ).items
    except Exception:
        return None

    totals = {}

    for pod in pods:
        node_name = pod.spec.node_name

        if not node_name:
            continue

        total = totals.setdefault(
            node_name,
            {"cpu": 0.0, "memory": 0.0, **dict.fromkeys(GPU_RESOURCES, 0)},
        )

        load = pod_requests(pod)
        used = pod_usage.get((pod.metadata.namespace, pod.metadata.name))

        if used:
            load["cpu"] = max(load["cpu"], used["cpu"])
            load["memory"] = max(load["memory"], used["memory"])

        for key, value in load.items():
            total[key] += value

    return totals

def get_pod_usage():
    try:
        metrics = kubernetes.client.CustomObjectsApi(
        ).list_cluster_custom_object(
            "metrics.k8s.io", "v1beta1", "pods",
        )
    except Exception:
        return {}

    return {
        (item["metadata"]["namespace"], item["metadata"]["name"]): {
            "cpu": sum(
                cpu_quantity(container["usage"]["cpu"])
                for container in item.get("containers", [])
            ),
            "memory": sum(
                memory_quantity_gib(container["usage"]["memory"])
                for container in item.get("containers", [])
            ),
        }
        for item in metrics.get("items", [])
    }

def get_node_usage():
    try:
        metrics = kubernetes.client.CustomObjectsApi(
        ).list_cluster_custom_object(
            "metrics.k8s.io", "v1beta1", "nodes",
        )
    except Exception:
        return {}

    return {
        item["metadata"]["name"]: {
            "cpu": cpu_quantity(item["usage"]["cpu"]),
            "memory": memory_quantity_gib(item["usage"]["memory"]),
        }
        for item in metrics.get("items", [])
    }

def get_node_inventory(detailed=False):
    inventory = {}

    api = kubernetes_api()
    pod_load = (
        get_node_pod_load(api, get_pod_usage()) if detailed else None
    )
    usage = get_node_usage() if detailed else {}

    for node in api.list_node().items:
        allocatable = node.status.allocatable or {}
        capacity = node.status.capacity or {}
        labels = node.metadata.labels or {}
        annotations = node.metadata.annotations or {}
        node_info = node.status.node_info

        hostname = node_hostname(node)
        cap_gpu = gpu_counts(capacity)

        m0net_labels = {
            key: value
            for key, value in labels.items()
            if key.startswith("m0net/")
        }

        all_cpu = cpu_quantity(allocatable.get("cpu", 0))
        all_memory = memory_quantity_gib(allocatable.get("memory", 0))
        all_gpu = gpu_counts(allocatable)
        node_usage = usage.get(node.metadata.name)

        if pod_load is None or not node_is_ready(node):
            ava_cpu = ava_memory = ava_gpu = use_gpu = None
        else:
            loaded = pod_load.get(
                node.metadata.name,
                {"cpu": 0.0, "memory": 0.0, **dict.fromkeys(GPU_RESOURCES, 0)},
            )
            ava_cpu = max(0.0, all_cpu - loaded["cpu"])
            ava_memory = max(0.0, all_memory - loaded["memory"])
            ava_gpu = {
                resource: max(0, count - loaded[resource])
                for resource, count in all_gpu.items()
            }
            use_gpu = {
                resource: count - ava_gpu[resource]
                for resource, count in all_gpu.items()
            }

            if node_usage:
                ava_cpu = min(
                    ava_cpu, max(0.0, all_cpu - node_usage["cpu"])
                )
                ava_memory = min(
                    ava_memory,
                    max(0.0, all_memory - node_usage["memory"]),
                )

        inventory[hostname] = {
            "name": node.metadata.name,
            "hostname": hostname,
            "ready": node_is_ready(node),
            "unschedulable": bool(node.spec.unschedulable),
            "taints": node_taints(node),
            "labels": labels,
            "m0net_labels": m0net_labels,
            "annotations": annotations,
            "architecture": node_info.architecture or "unknown",
            "cpu_model": annotations.get(
                CPU_MODEL_ANNOTATION,
                "unknown",
            ),
            "threads_per_core": threads_per_core(annotations),
            "gpu_model": annotations.get(
                GPU_MODEL_ANNOTATION,
                "unknown" if cap_gpu else "No GPU",
            ),
            "os_image": node_info.os_image or "unknown",
            "cap_cpu": cpu_quantity(
                capacity.get("cpu", 0)
            ),
            "cap_memory": memory_quantity_gib(
                capacity.get("memory", 0)
            ),
            "cap_gpu": cap_gpu,
            "all_cpu": cpu_quantity(
                allocatable.get("cpu", 0)
            ),
            "all_memory": memory_quantity_gib(
                allocatable.get("memory", 0)
            ),
            "all_gpu": all_gpu,
            "use_cpu": node_usage["cpu"] if node_usage else None,
            "use_memory": node_usage["memory"] if node_usage else None,
            "use_gpu": use_gpu,
            "ava_cpu": ava_cpu,
            "ava_memory": ava_memory,
            "ava_gpu": ava_gpu,
        }

    return inventory

def get_node_or_raise(hostname):
    node = get_node_inventory().get(hostname)

    if node is None:
        raise ValueError(
            f"Selected Kubernetes node does not exist: {hostname}"
        )

    if not node["ready"]:
        raise ValueError(
            f"Selected node '{hostname}' is not Ready."
        )

    if node["unschedulable"]:
        raise ValueError(
            f"Selected node '{hostname}' has scheduling disabled."
        )

    return node

# -----------------------------------------------------------------------------
# HTML generation
# -----------------------------------------------------------------------------

def render_image_options(include_cuda):
    groups = list(IMAGE_GROUPS)

    if include_cuda:
        groups.append(("CUDA", CUDA_IMAGES))

    rendered_groups = []

    for label, images in groups:
        options = []

        for image, description in images:
            selected = " selected" if image == DEFAULT_IMAGE else ""

            options.append(
                f'<option value="{html.escape(image, quote=True)}"'
                f"{selected}>"
                f"{html.escape(description)}"
                "</option>"
            )

        rendered_groups.append(
            f'<optgroup label="{html.escape(label, quote=True)}">'
            f"{''.join(options)}"
            "</optgroup>"
        )

    return "".join(rendered_groups)

def render_node_option(node):
    hostname = html.escape(node["hostname"], quote=True)
    short_name = html.escape(node["name"].partition(".")[0])

    return f'<option value="{hostname}">{short_name}</option>'

def browser_node_data(node):
    return {
        "name": node["name"],
        "lab": any(
            node["labels"].get(key) == value
            for key, value in JUPYTERLAB_LABELS
        ),
        "ready": node["ready"],
        "unschedulable": node["unschedulable"],
        "taints": node["taints"],
        "labels": node["labels"],
        "m0net_labels": node["m0net_labels"],
        "annotations": node["annotations"],
        "architecture": node["architecture"],
        "cpuModel": node["cpu_model"],
        "threadsPerCore": node["threads_per_core"],
        "gpuModel": node["gpu_model"],
        "osImage": node["os_image"],
        "cpuFree": node["all_cpu"] <= CPUFREE_MAX_CPU,
        "capCpu": node["cap_cpu"],
        "capMemory": node["cap_memory"],
        "capGpu": node["cap_gpu"],
        "allCpu": node["all_cpu"],
        "allMemory": node["all_memory"],
        "allGpu": node["all_gpu"],
        "useCpu": node["use_cpu"],
        "useMemory": node["use_memory"],
        "useGpu": node["use_gpu"],
        "avaCpu": node["ava_cpu"],
        "avaMemory": node["ava_memory"],
        "avaGpu": node["ava_gpu"],
    }

def dynamic_options_form(spawner):
    try:
        nodes = sorted(
            get_node_inventory(detailed=True).values(),
            key=lambda node: node["name"],
        )
    except Exception as exc:
        return f"""
        <div class="alert alert-danger">
            <strong>Unable to obtain Kubernetes nodes:</strong>
            {html.escape(str(exc))}
        </div>
        """

    if not nodes:
        return """
        <div class="alert alert-danger">
            No Kubernetes nodes are available.
        </div>
        """

    node_options = "".join(
        render_node_option(node)
        for node in nodes
    )

    browser_inventory = {
        node["hostname"]: browser_node_data(node)
        for node in nodes
    }

    inventory_json = html.escape(
        json.dumps(browser_inventory),
        quote=True,
    )

    image_options = render_image_options(
        include_cuda=any(node["all_gpu"] for node in nodes)
    )

    return f"""
    <style>
        .resource-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .resource-row > label {{
            width: 120px;
            text-align: right;
        }}

        @media (max-width: 576px) {{
            .resource-row {{
                flex-direction: column;
                align-items: stretch;
                gap: 4px;
            }}

            .resource-row > label {{
                width: auto;
                text-align: left;
            }}
        }}

        .resource-memory {{
            display: flex;
            align-items: center;
            gap: 6px;
            width: 100%;
        }}

        #node-summary {{
            margin: 0;
            overflow-x: auto;
            overflow-wrap: anywhere;
        }}

        #node-summary table,
        #node-summary th,
        #node-summary td {{
            background-color: transparent;
        }}

        #node-summary .table > thead > tr > th,
        #node-summary .table > tbody > tr > th,
        #node-summary .table > tbody > tr > td {{
            border-color: rgba(0, 0, 0, 0.15);
        }}

        #node-summary table {{
            margin-bottom: 8px;
        }}

        #node-summary td {{
            text-align: right;
            white-space: nowrap;
        }}
    </style>

    <div class="panel panel-default">
        <div class="panel-heading">
            <strong>Server resources</strong>
        </div>

        <div class="panel-body">
          <div class="spawn-layout" id="spawn-layout">
           <div class="spawn-fields">
            <div class="form-group resource-row">
                <label for="node" class="control-label">Node</label>
                <select
                    id="node"
                    name="node"
                    class="form-control"
                    required
                >
                    {node_options}
                </select>
            </div>

            <div class="form-group resource-row">
                <label for="image" class="control-label">Image</label>
                <select
                    id="image"
                    name="image"
                    class="form-control"
                    required
                >
                    {image_options}
                </select>
            </div>

            <div class="form-group resource-row">
                <label
                    for="resource-profile"
                    class="control-label"
                >
                    Server size
                </label>

                <select
                    id="resource-profile"
                    class="form-control"
                    required
                ></select>
            </div>

            <div id="cpu-row" class="form-group resource-row" hidden>
                <label for="cpu" class="control-label">CPU</label>
                <input
                    id="cpu"
                    name="cpu"
                    type="number"
                    min="0"
                    step="1"
                    class="form-control"
                    required
                >
            </div>

            <div id="memory-row" class="form-group resource-row" hidden>
                <label for="mem" class="control-label">Memory</label>

                <div class="resource-memory">
                    <input
                        id="mem"
                        name="mem"
                        type="number"
                        min="0"
                        step="1"
                        class="form-control"
                        required
                    >
                    <span>GiB</span>
                </div>
            </div>

            <div id="gpu-row" class="form-group resource-row">
                <label for="gpu" class="control-label">GPU</label>
                <select
                    id="gpu"
                    name="gpu"
                    class="form-control"
                    required
                ></select>
            </div>
           </div>

           <div class="spawn-summary" id="summary-slot">
            <div id="node-summary" class="alert alert-info"></div>
           </div>
          </div>
        </div>
    </div>

    <div
        id="node-inventory"
        data-inventory="{inventory_json}"
        hidden
    ></div>

    <script>
    (() => {{
        const CUSTOM_PROFILE = "custom";
        const MEMORY_MARGIN = {MEMORY_SAFETY_MARGIN_GIB};

        const byId = (id) => document.getElementById(id);
        const fmtGpu = (counts) => (
            counts === null
                ? "n/a"
                : Object.entries(counts)
                    .map(([resource, count]) => `${{count}} × ${{resource}}`)
                    .join(", ") || "0"
        );

        const gpuTotal = (counts) => (
            counts === null
                ? null
                : Object.values(counts).reduce((a, b) => a + b, 0)
        );

        const el = (tag, text = null) => {{
            const element = document.createElement(tag);

            if (text !== null) {{
                element.textContent = text;
            }}

            return element;
        }};

        const ARCHITECTURES = {{ amd64: "x86-64", arm64: "ARM64" }};
        const archName = (architecture) => (
            ARCHITECTURES[architecture] || architecture
        );

        const fmt = (value, digits = 2) => (
            value === null ? "n/a" : value.toFixed(digits)
        );

        const wholeCpu = (resources) => Math.max(
            1,
            Math.floor(resources.allCpu)
        );
        const wholeMemory = (resources) => Math.max(
            1,
            Math.floor(resources.allMemory)
        );

        const inventory = JSON.parse(
            byId("node-inventory").dataset.inventory
        );

        const nodeSelect = byId("node");
        const profileSelect = byId("resource-profile");
        const cpuInput = byId("cpu");
        const memoryInput = byId("mem");
        const gpuSelect = byId("gpu");
        const summary = byId("node-summary");
        const cpuRow = byId("cpu-row");
        const memoryRow = byId("memory-row");
        const gpuRow = byId("gpu-row");
        const summarySlot = byId("summary-slot");

        function addOption(select, value, text, selected = false) {{
            const option = new Option(text, value, false, selected);
            select.add(option);
            return option;
        }}

        function divisors(value) {{
            value = Math.floor(Number(value));

            if (!Number.isFinite(value) || value < 1) {{
                return [1];
            }}

            const lower = [];
            const upper = [];

            for (let divisor = 1;
                 divisor <= Math.sqrt(value);
                 divisor += 1) {{
                if (value % divisor !== 0) {{
                    continue;
                }}

                lower.push(divisor);

                const paired = value / divisor;

                if (paired !== divisor) {{
                    upper.push(paired);
                }}
            }}

            return lower.concat(upper.reverse());
        }}

        function resourceProfiles(resources) {{
            if (resources.cpuFree) {{
                return [{{
                    value: "server-nolimit",
                    denominator: 1,
                    cpu: 0,
                    memory: Math.max(
                        1,
                        Math.floor(wholeMemory(resources) - MEMORY_MARGIN)
                    ),
                }}];
            }}

            const cpuLimit = Math.max(
                1,
                Math.floor(wholeCpu(resources) / resources.threadsPerCore)
            );

            const memoryLimit = Math.max(
                1,
                Math.floor(wholeMemory(resources) - MEMORY_MARGIN)
            );

            return divisors(cpuLimit).map((cpu) => {{
                const denominator = cpuLimit / cpu;
                const memory = Math.max(
                    1,
                    Math.floor(memoryLimit * cpu / cpuLimit)
                );

                return {{
                    value: `server-1-${{denominator}}`,
                    denominator,
                    cpu,
                    memory,
                }};
            }});
        }}

        function applyProfile() {{
            const isCustom = profileSelect.value === CUSTOM_PROFILE;

            cpuRow.hidden = !isCustom;
            memoryRow.hidden = !isCustom;

            if (isCustom) {{
                return;
            }}

            const option = profileSelect.selectedOptions[0];

            cpuInput.value = option.dataset.cpu;
            memoryInput.value = option.dataset.memory;
        }}

        function markCustom() {{
            profileSelect.value = CUSTOM_PROFILE;
        }}

        function usageTable(resources) {{
            const table = el("table");
            table.className = "table table-condensed";

            const head = table.createTHead().insertRow();

            ["", "CPU", "RAM (GiB)", "GPU"].forEach((text) => {{
                head.appendChild(el("th", text));
            }});

            const rows = [
                [
                    "Capacity",
                    fmt(resources.capCpu),
                    fmt(resources.capMemory),
                    fmtGpu(resources.capGpu),
                ],
                [
                    "Allocatable",
                    fmt(resources.allCpu),
                    fmt(resources.allMemory),
                    fmtGpu(resources.allGpu),
                ],
                [
                    "Used",
                    fmt(resources.useCpu),
                    fmt(resources.useMemory),
                    fmtGpu(resources.useGpu),
                ],
                [
                    "Available",
                    fmt(resources.avaCpu),
                    fmt(resources.avaMemory),
                    fmtGpu(resources.avaGpu),
                ],
            ];

            const body = table.createTBody();

            rows.forEach((cells) => {{
                const row = body.insertRow();

                cells.forEach((text, index) => {{
                    row.appendChild(el(index === 0 ? "th" : "td", text));
                }});
            }});

            return table;
        }}

        function infoLines(resources, taints) {{
            const taintText = taints.length > 0
                ? taints.map((taint) => {{
                    const value = taint.value
                        ? `=${{taint.value}}`
                        : "";

                    const effect = taint.effect
                        ? `:${{taint.effect}}`
                        : "";

                    return `${{taint.key}}${{value}}${{effect}}`;
                }}).join(", ")
                : "None";

            const m0netLabelText = Object.entries(resources.m0net_labels || {{}})
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([key, value]) => `${{key}}=${{value}}`)
                .join(", ") || "None";

            return [
                ["CPU", `${{resources.cpuModel}} (${{archName(resources.architecture)}})`],
                ["Threads/core", String(resources.threadsPerCore)],
                ["GPU", resources.gpuModel],
                ["OS", resources.osImage],
                ["m0net labels", m0netLabelText],
                ["Taints", taintText],
            ].map(([label, value]) => {{
                const line = el("div");
                line.appendChild(el("strong", `${{label}}: `));
                line.appendChild(document.createTextNode(value));
                return line;
            }});
        }}

        // open: ready and takes labs; reserved: ready, other roles;
        // blocked: not ready, unschedulable or with a hard taint.
        function nodeState(resources) {{
            const hardTaint = resources.taints.some(
                (taint) => taint.effect !== "PreferNoSchedule"
            );

            if (!resources.ready || resources.unschedulable || hardTaint) {{
                return "blocked";
            }}

            return resources.lab ? "open" : "reserved";
        }}

        const compact = (value) => (
            value === null ? "-" : String(Number(value.toFixed(1)))
        );

        function nodeLabel(resources) {{
            const gpuAvailable = gpuTotal(resources.avaGpu);
            // Nominal size: the OS reports a bit less than the installed RAM.
            const memoryCapacity = Math.ceil(resources.capMemory / 4) * 4;

            return (
                `${{resources.name.split(".")[0]}} · ` +
                `${{nodeState(resources)}} · ` +
                `CPU ${{compact(resources.avaCpu)}}/` +
                `${{compact(resources.capCpu)}} · ` +
                `RAM ${{compact(resources.avaMemory)}}/${{memoryCapacity}} · ` +
                `GPU ${{gpuAvailable === null ? "-" : gpuAvailable}}/` +
                `${{gpuTotal(resources.capGpu)}}`
            );
        }}

        function placeSummary() {{
            const form = nodeSelect.form;

            if (!form) {{
                return;
            }}

            const slot = el("div");
            slot.style.marginTop = "15px";
            slot.appendChild(summary);
            form.after(slot);
            summarySlot.hidden = true;
        }}

        function labelNodes() {{
            Array.from(nodeSelect.options).forEach((option) => {{
                option.textContent = nodeLabel(inventory[option.value]);
            }});
        }}

        function updateResources() {{
            const resources = inventory[nodeSelect.value];

            profileSelect.replaceChildren();
            gpuSelect.replaceChildren();
            const gpus = Object.entries(resources.allGpu);
            gpuRow.hidden = gpus.length === 0;

            const profiles = resourceProfiles(resources);

            profiles.forEach((profile, index) => {{
                const bound = profiles.length === 1 ? ""
                    : index === 0 ? " (min)"
                    : index === profiles.length - 1 ? " (max)"
                    : "";

                const option = addOption(
                    profileSelect,
                    profile.value,
                    (
                        resources.cpuFree
                            ? "no CPU limit"
                            : `${{profile.cpu}} CPU`
                    ) + ` · ${{profile.memory}} GiB RAM${{bound}}`,
                    index === 0
                );

                option.dataset.cpu = profile.cpu;
                option.dataset.memory = profile.memory;
            }});

            addOption(
                profileSelect,
                CUSTOM_PROFILE,
                "Custom"
            );

            cpuInput.max = wholeCpu(resources);
            memoryInput.max = wholeMemory(resources);

            applyProfile();

            addOption(gpuSelect, "0", "0 GPU", true);

            gpus.forEach(([resource, total]) => {{
                for (let count = 1; count <= total; count += 1) {{
                    addOption(
                        gpuSelect,
                        `${{resource}}=${{count}}`,
                        `${{count}} × ${{resource}}`
                    );
                }}
            }});

            const taints = Array.isArray(resources.taints)
                ? resources.taints
                : [];

            if (!resources.ready || resources.unschedulable) {{
                summary.className = "alert alert-danger";
            }} else if (taints.length > 0) {{
                summary.className = "alert alert-warning";
            }} else {{
                summary.className = "alert alert-info";
            }}

            summary.replaceChildren(
                usageTable(resources),
                ...infoLines(resources, taints)
            );
        }}

        profileSelect.addEventListener("change", applyProfile);
        cpuInput.addEventListener("input", markCustom);
        memoryInput.addEventListener("input", markCustom);
        nodeSelect.addEventListener("change", updateResources);

        labelNodes();

        const firstOpen = Array.from(nodeSelect.options).find(
            (option) => nodeState(inventory[option.value]) === "open"
        );

        if (firstOpen) {{
            nodeSelect.value = firstOpen.value;
        }}

        placeSummary();
        updateResources();
    }})();
    </script>
    """

c.KubeSpawner.options_form = dynamic_options_form

# -----------------------------------------------------------------------------
# Form validation
# -----------------------------------------------------------------------------

def form_value(formdata, name, default=""):
    values = formdata.get(name, [default])
    return str(values[0]).strip()

def parse_integer(value, label, minimum=0):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid {label} value: {value}"
        ) from exc

    if parsed < minimum:
        raise ValueError(
            f"{label} must be at least {minimum}."
        )

    return parsed

def validate_resources(node, cpu, memory_gib, gpu):
    limits = (
        ("CPU", cpu, node["all_cpu"]),
        ("memory", memory_gib, node["all_memory"]),
        *(
            (resource, count, node["all_gpu"].get(resource, 0))
            for resource, count in gpu.items()
        ),
    )

    for label, requested, available in limits:
        if requested > available:
            raise ValueError(
                f"Requested {label} ({requested}) exceeds "
                f"node '{node['hostname']}' allocatable {label} "
                f"({available:g})."
            )

def parse_gpu(value):
    """Form value "0" or "<resource>=<count>" -> {resource: count}."""
    if value in ("", "0"):
        return {}

    resource, _, count = value.rpartition("=")

    if resource not in GPU_RESOURCES:
        raise ValueError(f"Invalid GPU resource: {resource}")

    return {resource: parse_integer(count, "GPU", minimum=1)}

def options_from_form(formdata):
    hostname = form_value(formdata, "node")
    image = form_value(formdata, "image", DEFAULT_IMAGE)
    cpu = parse_integer(
        form_value(formdata, "cpu", "1"),
        "CPU",
        minimum=0,
    )
    memory_gib = parse_integer(
        form_value(formdata, "mem", "2"),
        "memory",
        minimum=0,
    )
    gpu = parse_gpu(form_value(formdata, "gpu", "0"))

    if not hostname:
        raise ValueError(
            "A Kubernetes node must be selected."
        )

    if not image.startswith(ALLOWED_IMAGE_PREFIXES):
        raise ValueError(
            f"Image '{image}' is not allowed."
        )

    if "cuda" in image.lower() and not gpu:
        raise ValueError(
            "The selected CUDA image requires at least one GPU."
        )

    node = get_node_or_raise(hostname)
    validate_resources(node, cpu, memory_gib, gpu)

    return {
        "node": hostname,
        "image": image,
        "cpu": cpu,
        "memory_gib": memory_gib,
        "gpu": gpu,
    }


c.KubeSpawner.options_from_form = options_from_form

# -----------------------------------------------------------------------------
# Apply user selection
# -----------------------------------------------------------------------------

def apply_user_options(spawner, options):
    node = get_node_or_raise(options["node"])

    validate_resources(
        node=node,
        cpu=options["cpu"],
        memory_gib=options["memory_gib"],
        gpu=options["gpu"],
    )

    cpu = options["cpu"]
    memory_bytes = options["memory_gib"] * 1024**3
    gpu = options["gpu"]

    spawner.image = options["image"]

    spawner.cpu_guarantee = cpu if cpu > 0 else None
    spawner.cpu_limit = cpu if cpu > 0 else None
    spawner.mem_guarantee = memory_bytes if memory_bytes > 0 else None
    # +1 byte: limit differs from guarantee on purpose, so the pod is Burstable instead of Guaranteed QoS.
    spawner.mem_limit = 1 + memory_bytes if memory_bytes > 0 else None

    spawner.node_selector = {
        HOSTNAME_LABEL: options["node"],
    }
    spawner.node_affinity_required = [
        {
            "matchExpressions": [
                {
                    "key": key,
                    "operator": "In",
                    "values": [value],
                },
            ],
        }
        for key, value in JUPYTERLAB_LABELS
    ]

    short_hostname = options["node"].partition(".")[0]
    pvc_name = f"work-{spawner.user.name}-{short_hostname}"

    spawner.pvc_name_template = pvc_name
    spawner.pvc_name = pvc_name

    spawner.volumes = [
        *(spawner.volumes or []),
        {
            "name": "work",
            "persistentVolumeClaim": {
                "claimName": pvc_name,
            },
        },
    ]

    spawner.volume_mounts = [
        *(spawner.volume_mounts or []),
        {
            "name": "work",
            "mountPath": "/home/jovyan/work",
        },
    ]

    spawner.extra_resource_guarantees = dict(gpu)
    spawner.extra_resource_limits = dict(gpu)

c.KubeSpawner.apply_user_options = apply_user_options

# -----------------------------------------------------------------------------
# Services
# -----------------------------------------------------------------------------

c.JupyterHub.load_groups = {
    "idle-2h": [],
    "idle-8h": [],
    "idle-24h": [],
    "idle-72h": [],
}

c.JupyterHub.services = [
    {
        "name": "jupyterhub-idle-culler-service",
        "command": [
            sys.executable,
            "-m",
            "jupyterhub_idle_culler",
            "--config=/etc/jupyterhub/idle_culler_config.py",
        ],
    },
]

c.JupyterHub.load_roles = [
    {
        "name": "jupyterhub-idle-culler-role",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:users:groups",
            "read:servers",
            "delete:servers",
        ],
        "services": ["jupyterhub-idle-culler-service"],
    },
]

# eof