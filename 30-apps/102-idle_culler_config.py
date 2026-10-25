# idle_culler_config.py
# Loaded by jupyterhub_idle_culler (>= 2.0) through --config.
import json
import logging
import os
import re
from urllib.parse import quote, unquote

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

GROUP_PATTERN = re.compile(r"^idle-(\d+)h$")
log = logging.getLogger("IdleCuller")

async def group_timeout(user):
    response = await AsyncHTTPClient().fetch(
        HTTPRequest(
            f"{os.environ['JUPYTERHUB_API_URL']}/users/{quote(user)}",
            headers={
                "Authorization": f"token {os.environ['JUPYTERHUB_API_TOKEN']}",
            },
        )
    )

    groups = json.loads(response.body).get("groups", [])
    matches = (GROUP_PATTERN.match(group) for group in groups)
    hours = [int(match.group(1)) for match in matches if match]

    return max(hours, default=None)

async def cull_arbiter(inactive, inactive_limit, server, **kwargs):
    if inactive is None:
        return False

    user = unquote(server["url"].strip("/").split("/")[1])  # /user/<name>/

    try:
        hours = await group_timeout(user)
    except Exception:
        log.exception("Could not read the groups of %s; not culling", user)
        return False

    limit = inactive_limit if hours is None else hours * 3600

    return inactive.total_seconds() >= limit

c.IdleCuller.cull_arbiter_hook = cull_arbiter

# eof
