# jupyterhub_config.py
import html
import json
import math
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
c.JupyterHub.allow_named_servers = True

# -----------------------------------------------------------------------------
# KubeSpawner defaults
# -----------------------------------------------------------------------------

c.KubeSpawner.image_pull_policy = "IfNotPresent"

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
GPU_MODEL_ANNOTATION = "gpu-model"
# kubectl annotate node $(hostname --long) gpu-model-
# kubectl annotate node $(hostname --long) gpu-model="GPU Model"
JUPYTERLAB_LABEL = "m0net/run.jupyterlab"
JUPYTERLAB_LABEL_VALUE = "true"

MEMORY_SAFETY_MARGIN_GIB = 2

ALLOWED_IMAGE_PREFIXES = (
    "ghcr.io/rlinfati/",
    "quay.io/jupyter/",
)

DEFAULT_IMAGE = (
    "ghcr.io/rlinfati/"
    "lab0-container:jupyter-lab-julia-1.12"
)

IMAGE_GROUPS = (
    (
        "rlinfati/lab0",
        (
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.13",
                "Julia 1.13 alpha/beta/rc",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.12",
                "Julia 1.12 stable",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-julia-1.10",
                "Julia 1.10 LTS",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-anaconda-latest",
                "Anaconda",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-devcpp-latest",
                "devcpp",
            ),
            (
                "ghcr.io/rlinfati/"
                "lab0-container:jupyter-lab-base-latest",
                "base",
            ),
        ),
    ),
    (
        "jupyter/notebook",
        (
            (
                "quay.io/jupyter/julia-notebook:latest",
                "Julia",
            ),
            (
                "quay.io/jupyter/scipy-notebook:latest",
                "SciPy",
            ),
            (
                "quay.io/jupyter/r-notebook:latest",
                "R",
            ),
            (
                "quay.io/jupyter/pytorch-notebook:latest",
                "PyTorch",
            ),
            (
                "quay.io/jupyter/tensorflow-notebook:latest",
                "TensorFlow",
            ),
        ),
    ),
)

CUDA_IMAGES = (
    (
        "ghcr.io/rlinfati/"
        "lab0-container:jupyter-lab-juliacuda-1.10",
        "[lab0] Julia 1.10 + CUDA",
    ),
    (
        "quay.io/jupyter/pytorch-notebook:cuda13-latest",
        "[jupyter] PyTorch + CUDA",
    ),
    (
        "quay.io/jupyter/tensorflow-notebook:cuda-latest",
        "[jupyter] TensorFlow + CUDA",
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

    if value.endswith("m"):
        return float(value[:-1]) / 1000

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

def rounded_memory(value, step=8):
    value = float(value)

    if value <= 0:
        return 0

    return math.ceil(value / step) * step

def get_node_inventory():
    inventory = {}

    for node in kubernetes_api().list_node().items:
        allocatable = node.status.allocatable or {}
        capacity = node.status.capacity or {}
        labels = node.metadata.labels or {}
        annotations = node.metadata.annotations or {}
        node_info = node.status.node_info

        hostname = node_hostname(node)
        total_gpu = int(capacity.get("nvidia.com/gpu", 0))

        m0net_labels = {
            key: value
            for key, value in labels.items()
            if key.startswith("m0net/")
        }        

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
            "gpu_model": annotations.get(
                GPU_MODEL_ANNOTATION,
                "No GPU" if total_gpu == 0 else "unknown",
            ),
            "os_image": node_info.os_image or "unknown",
            "alloc_cpu": cpu_quantity(
                allocatable.get("cpu", 0)
            ),
            "total_cpu": cpu_quantity(
                capacity.get("cpu", 0)
            ),
            "alloc_memory": memory_quantity_gib(
                allocatable.get("memory", 0)
            ),
            "total_memory": memory_quantity_gib(
                capacity.get("memory", 0)
            ),
            "alloc_gpu": int(
                allocatable.get("nvidia.com/gpu", 0)
            ),
            "total_gpu": total_gpu,
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
        groups.append(("NVIDIA/CUDA", CUDA_IMAGES))

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
    statuses = []

    if node["ready"]:
        statuses.append("Ready")
    else:
        statuses.append("Not Ready")

    if node["unschedulable"]:
        statuses.append("unschedulable")

    if node["taints"]:
        statuses.append("taints")

    label = (
        f"{node['name']} [{', '.join(statuses)}] — "
        f"CPU {node['total_cpu']:g}, "
        f"RAM {rounded_memory(node['total_memory'])} GiB, "
        f"GPU {node['total_gpu']}"
    )

    disabled = (
        " disabled"
        if not node["ready"] or node["unschedulable"]
        else ""
    )

    hostname = html.escape(node["hostname"], quote=True)

    return (
        f'<option value="{hostname}"{disabled}>'
        f"{html.escape(label)}"
        "</option>"
    )

def browser_node_data(node):
    return {
        "ready": node["ready"],
        "unschedulable": node["unschedulable"],
        "taints": node["taints"],
        "labels": node["labels"],
        "m0net_labels": node["m0net_labels"],
        "annotations": node["annotations"],
        "architecture": node["architecture"],
        "cpuModel": node["cpu_model"],
        "gpuModel": node["gpu_model"],
        "osImage": node["os_image"],
        "cpu": max(1, math.floor(node["alloc_cpu"])),
        "memory": max(1, math.floor(node["alloc_memory"])),
        "gpu": node["alloc_gpu"],
        "allocCpu": node["alloc_cpu"],
        "totalCpu": node["total_cpu"],
        "allocMemory": f"{node['alloc_memory']:.2f}",
        "totalMemory": f"{node['total_memory']:.2f}",
        "allocGpu": node["alloc_gpu"],
        "totalGpu": node["total_gpu"],
    }

def dynamic_options_form(spawner):
    try:
        nodes = sorted(
            get_node_inventory().values(),
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
        include_cuda=any(node["alloc_gpu"] > 0 for node in nodes)
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

        .resource-memory {{
            display: flex;
            align-items: center;
            gap: 6px;
            width: 100%;
        }}

        #node-summary {{
            margin-left: 130px;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }}
    </style>

    <div class="panel panel-default">
        <div class="panel-heading">
            <strong>Server resources</strong>
        </div>

        <div class="panel-body">
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

            <div id="node-summary" class="alert alert-info"></div>

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
            const cpuLimit = Math.max(
                1,
                Math.floor(resources.cpu / 2)
            );

            const memoryLimit = Math.max(
                1,
                Math.floor(resources.memory - MEMORY_MARGIN)
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

        function updateResources() {{
            const resources = inventory[nodeSelect.value];

            profileSelect.replaceChildren();
            gpuSelect.replaceChildren();
            const hasGpu = resources.gpu > 0;
            gpuRow.hidden = !hasGpu;

            resourceProfiles(resources).forEach((profile, index) => {{
                const option = addOption(
                    profileSelect,
                    profile.value,
                    `1/${{profile.denominator}} server — ` +
                    `${{profile.cpu}} CPU — ` +
                    `${{profile.memory}} GiB RAM`,
                    index === 0
                );

                option.dataset.cpu = profile.cpu;
                option.dataset.memory = profile.memory;
            }});

            addOption(
                profileSelect,
                CUSTOM_PROFILE,
                "Custom server resources"
            );

            cpuInput.max = Math.max(1, Math.floor(resources.cpu));
            memoryInput.max = Math.max(
                1,
                Math.floor(resources.memory)
            );

            applyProfile();

            for (let gpu = 0; gpu <= resources.gpu; gpu += 1) {{
                addOption(
                    gpuSelect,
                    String(gpu),
                    `${{gpu}} GPU`,
                    gpu === 0
                );
            }}

            let status;

            if (!resources.ready) {{
                status = "Not Ready";
            }} else if (resources.unschedulable) {{
                status = "Ready, unschedulable";
            }} else {{
                status = "Ready";
            }}

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

            summary.textContent = [
                `Status: ${{status}}`,
                `Architecture: ${{resources.architecture}}`,
                `CPU model: ${{resources.cpuModel}}`,
                `GPU model: ${{resources.gpuModel}}`,
                `OS image: ${{resources.osImage}}`,
                (
                    `Capacity: ${{resources.totalCpu}} CPU, ` +
                    `${{resources.totalMemory}} GiB RAM, ` +
                    `${{resources.totalGpu}} GPU`
                ),
                (
                    `Allocatable: ${{resources.allocCpu}} CPU, ` +
                    `${{resources.allocMemory}} GiB RAM, ` +
                    `${{resources.allocGpu}} GPU`
                ),
                (
                    `Available: iii CPU, ` +
                    `jjj GiB RAM, ` +
                    `kkk GPU`
                ),
                `m0net Labels: ${{m0netLabelText}}`,
                `Taints: ${{taintText}}`,
            ].join("\\n");            
        }}

        profileSelect.addEventListener("change", applyProfile);
        cpuInput.addEventListener("input", markCustom);
        memoryInput.addEventListener("input", markCustom);
        nodeSelect.addEventListener("change", updateResources);

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
        ("CPU", cpu, node["alloc_cpu"]),
        ("memory", memory_gib, node["alloc_memory"]),
        ("GPU", gpu, node["alloc_gpu"]),
    )

    for label, requested, available in limits:
        if requested > available:
            raise ValueError(
                f"Requested {label} ({requested}) exceeds "
                f"node '{node['hostname']}' allocatable {label} "
                f"({available:g})."
            )

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
    gpu = parse_integer(
        form_value(formdata, "gpu", "0"),
        "GPU",
        minimum=0,
    )

    if not hostname:
        raise ValueError(
            "A Kubernetes node must be selected."
        )

    if not image.startswith(ALLOWED_IMAGE_PREFIXES):
        raise ValueError(
            f"Image '{image}' is not allowed."
        )

    if "cuda" in image.lower() and gpu == 0:
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
    spawner.mem_limit = memory_bytes if memory_bytes > 0 else None

    spawner.node_selector = {
        JUPYTERLAB_LABEL: JUPYTERLAB_LABEL_VALUE,
        HOSTNAME_LABEL: options["node"],
    }

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

    gpu_resources = (
        {"nvidia.com/gpu": gpu}
        if gpu > 0
        else {}
    )

    spawner.extra_resource_guarantees = gpu_resources.copy()
    spawner.extra_resource_limits = gpu_resources.copy()

c.KubeSpawner.apply_user_options = apply_user_options

# -----------------------------------------------------------------------------
# Services
# -----------------------------------------------------------------------------

c.JupyterHub.services = [
    {
        "name": "jupyterhub-idle-culler-service",
        "command": [
            sys.executable,
            "-m",
            "jupyterhub_idle_culler",
            "--timeout=7200",
        ],
        "admin": True,
    },
]

# eof