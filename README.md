# Logto Python SDK

[![Logto](https://img.shields.io/badge/for-logto-7958ff)](https://logto.io/)
[![Stable Version](https://img.shields.io/pypi/v/logto?label=stable)][PyPI Releases]
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/logto)][PyPI]
[![PyPI - License](https://img.shields.io/pypi/l/logto)][PyPI]
[![Discord](https://img.shields.io/discord/965845662535147551?color=5865f2&logo=discord&label=discord)][Discord]

## Usage

### Prerequisites

- Python 3.8 or higher
- A [Logto Cloud](https://logto.io/) account or a self-hosted Logto
- A Logto traditional web application created

If you don't have the Logto application created, please follow the [⚡ Get started](https://docs.logto.io/docs/tutorials/get-started/) guide to create one.

### Installation
```bash
pip install logto # or `poetry add logto` or whatever you use
```

### Init LogtoClient

```python
from logto import LogtoClient, LogtoConfig

client = LogtoClient(
    LogtoConfig(
        endpoint="https://you-logto-endpoint.app",  # Replace with your Logto endpoint
        appId="replace-with-your-app-id",
        appSecret="replace-with-your-app-secret",
    ),
)
```

### Sample code

See `samples/` directory for example usages.

### Documentation

While the dedicated documentation is still in progress, you can find other integration guides in [Integrate Logto in your application](https://docs.logto.io/docs/recipes/integrate-logto/).

Pick one you are most familiar with, read to know the basic concepts, then come back and check out `samples/` directory for example usages.

## Resources

[PyPI]: https://pypi.org/project/logto/
[PyPI Releases]: https://pypi.org/project/logto/#history
[Discord]: https://discord.gg/vRvwuwgpVX
