"""Utility helpers for interacting with the dbt MCP server."""
from __future__ import annotations

import asyncio
import ast
import json
import logging
import sys
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

TextContentType = Any  # fallback when MCP types are unavailable

# Set up logging for MCP operations
logger = logging.getLogger(__name__)


class McpUnavailableError(RuntimeError):
    """Raised when the dbt MCP server cannot be used."""


def _ensure_mcp_import_path() -> None:
    """Add the local dbt-mcp source directory to sys.path when present."""
    candidate = Path(__file__).resolve().parents[3] / "dbt_mcp" / "dbt-mcp" / "src"
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.append(str(candidate))


def _import_mcp_modules() -> tuple[Any, Any]:
    """Return the create_dbt_mcp factory and TextContent class when available."""
    _ensure_mcp_import_path()

    try:
        from dbt_mcp.mcp.server import create_dbt_mcp  # type: ignore
        from dbt_mcp.config.config import load_config  # type: ignore
        from mcp.types import TextContent  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise McpUnavailableError(
            "dbt MCP server dependencies are not available. Ensure the dbt-mcp "
            "package and its requirements (including `mcp`) are installed and that "
            "your Python version satisfies the dbt-mcp requirement (>=3.12)."
        ) from exc

    return create_dbt_mcp, TextContent, load_config


def _run_async(coro: Any) -> Any:
    """Execute an async coroutine from sync code, handling running loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    if loop.is_running():  # pragma: no cover - streamlit rarely has a running loop
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()

    return loop.run_until_complete(coro)


def _extract_text_content(contents: Iterable[Any], text_type: Any) -> str:
    """Combine tool responses into a single text payload."""
    chunks: List[str] = []
    for item in contents:
        if isinstance(item, text_type):
            text = getattr(item, "text", None)
            if text:
                chunks.append(text)
        else:
            text = getattr(item, "text", None)
            if text:
                chunks.append(text)
            else:
                chunks.append(str(item))
    return "\n".join(chunk for chunk in chunks if chunk).strip()


def _parse_jsonish(text: str, default: Any) -> Any:
    """Parse a string that may contain JSON; fall back to Python literals."""
    if not text:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try parsing multiple JSON objects separated by newlines
        try:
            # Find JSON objects using regex
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
            if len(json_objects) > 1:
                # Multiple JSON objects - parse each and return as list
                return [json.loads(obj) for obj in json_objects]
            elif len(json_objects) == 1:
                # Single JSON object
                return json.loads(json_objects[0])
        except (json.JSONDecodeError, IndexError):
            pass

        try:
            return ast.literal_eval(text)
        except Exception:
            return default


@lru_cache(maxsize=1)
def _get_mcp_client() -> Any:
    try:
        create_dbt_mcp, text_type, load_config = _import_mcp_modules()
        logger.info("Successfully imported MCP modules")
    except Exception as exc:
        logger.error(f"Failed to import MCP modules: {exc}")
        raise McpUnavailableError(f"Failed to import MCP modules: {exc}") from exc

    # Load environment variables from .env file
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        # Fallback to env.example if .env doesn't exist
        env_file = Path(__file__).parent.parent / "env.example"

    if env_file.exists():
        logger.info(f"Loading environment variables from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        logger.warning("No .env file found, using system environment variables")

    try:
        logger.info("Loading dbt MCP configuration")
        config = load_config()
        logger.info("Successfully loaded dbt MCP configuration")
    except Exception as exc:  # pragma: no cover - config validation
        logger.error(f"Failed to load dbt MCP configuration: {exc}")
        raise McpUnavailableError(f"Unable to load dbt MCP configuration: {exc}") from exc

    try:
        logger.info("Creating dbt MCP client")
        client = _run_async(create_dbt_mcp(config))
        client.__dict__.setdefault("_text_type", text_type)
        logger.info("Successfully created dbt MCP client")
        return client
    except Exception as exc:
        logger.error(f"Failed to create dbt MCP client: {exc}")
        raise McpUnavailableError(f"Failed to create dbt MCP client: {exc}") from exc


def is_mcp_available() -> bool:
    """Return True when the dbt MCP server can be instantiated."""
    try:
        _get_mcp_client()
    except McpUnavailableError:
        return False
    return True


def call_mcp_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Invoke a tool on the dbt MCP server and return the textual payload."""
    logger.info(f"MCP Tool Call: {name}")
    logger.debug(f"MCP Tool Arguments: {json.dumps(arguments, indent=2)}")

    client = _get_mcp_client()
    text_type = client.__dict__.get("_text_type", TextContentType)

    try:
        response = _run_async(client.call_tool(name, arguments))
        result = _extract_text_content(response, text_type)
        logger.info(f"MCP Tool Response Length: {len(result)} characters")
        logger.debug(f"MCP Tool Response: {result[:500]}{'...' if len(result) > 500 else ''}")
        return result
    except Exception as e:
        logger.error(f"MCP Tool Call Failed: {name} - {str(e)}")
        raise


def mcp_list_metrics() -> List[Dict[str, Any]]:
    logger.info("Fetching available metrics from MCP")
    payload = call_mcp_tool("list_metrics", {})
    parsed = _parse_jsonish(payload, default=None)
    if parsed is None:
        logger.error(f"MCP list_metrics returned no data: {payload}")
        raise RuntimeError(payload or "dbt MCP list_metrics returned no data.")
    if isinstance(parsed, list):
        logger.info(f"MCP returned {len(parsed)} metrics")
        return parsed
    logger.error(f"MCP list_metrics returned unexpected payload type: {type(parsed)}")
    raise RuntimeError(f"dbt MCP list_metrics returned unexpected payload: {payload}")


def mcp_get_dimensions(metric_names: List[str]) -> List[Dict[str, Any]]:
    logger.info(f"Fetching dimensions for metrics: {metric_names}")
    payload = call_mcp_tool("get_dimensions", {"metrics": metric_names})
    parsed = _parse_jsonish(payload, default=None)
    if parsed is None:
        logger.error(f"MCP get_dimensions returned no data: {payload}")
        raise RuntimeError(payload or "dbt MCP get_dimensions returned no data.")
    if isinstance(parsed, list):
        logger.info(f"MCP returned {len(parsed)} dimensions")
        return parsed
    logger.error(f"MCP get_dimensions returned unexpected payload type: {type(parsed)}")
    raise RuntimeError(f"dbt MCP get_dimensions returned unexpected payload: {payload}")


def mcp_query_metrics(payload: Dict[str, Any]) -> str:
    logger.info("Executing metrics query via MCP")
    logger.debug(f"Query payload: {json.dumps(payload, indent=2)}")
    result = call_mcp_tool("query_metrics", payload)
    # Check if the result is an error message
    if result.startswith("Expecting value") or result.startswith("Error") or result.startswith("errors"):
        logger.error(f"MCP query returned error: {result}")
        raise RuntimeError(f"dbt MCP query failed: {result}")
    logger.info("MCP query executed successfully")
    return result


def mcp_get_metric_sql(payload: Dict[str, Any]) -> str:
    """Request compiled SQL for a metric selection via the MCP."""
    result = call_mcp_tool("get_metrics_compiled_sql", payload)
    if not result:
        raise RuntimeError("dbt MCP get_metrics_compiled_sql returned no SQL text.")
    if result.lower().startswith("error"):
        raise RuntimeError(f"dbt MCP get_metrics_compiled_sql failed: {result}")
    return result