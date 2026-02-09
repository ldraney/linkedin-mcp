"""Tool registration — imports every tool module so @mcp.tool() decorators fire."""

from __future__ import annotations


def register_all_tools() -> None:
    """Import all tool modules, which register tools via the module-level @mcp.tool() decorators."""
    from . import auth  # noqa: F401
    from . import posts  # noqa: F401
    from . import media  # noqa: F401
    from . import engagement  # noqa: F401
    from . import users  # noqa: F401
    from . import scheduler  # noqa: F401
