import base64
from typing import Any

def urlsafeEncode(data: bytes) -> str:
  """
  Encode the given bytes to a URL-safe string.
  """
  return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def removeFalsyKeys(data: dict[str, Any]) -> dict[str, Any]:
  """
  Remove keys with falsy values from the given dictionary.
  """
  return {k: v for k, v in data.items() if v}
