import base64
from typing import Any, Dict


def urlsafeEncode(data: bytes) -> str:
    """
    Encode the given bytes to a URL-safe string.
    """
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def removeFalsyKeys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys with falsy values from the given dictionary.
    """
    return {k: v for k, v in data.items() if v}


OrganizationUrnPrefix = "urn:logto:organization:"
"""The prefix for Logto organization URNs."""


def buildOrganizationUrn(organizationId: str) -> str:
    """
    Build the organization URN from the organization ID.

    Example:
    ```python
    buildOrganizationUrn("1") # returns "urn:logto:organization:1"
    ```
    """
    return f"{OrganizationUrnPrefix}{organizationId}"
