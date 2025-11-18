from __future__ import annotations

import ipfshttpclient

from ..config import settings


def get_ipfs_client() -> ipfshttpclient.Client:
    """
    Connect to the configured IPFS API.
    """
    return ipfshttpclient.connect(settings.ipfs_api_url)

