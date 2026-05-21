# back/app/utils/assets.py
from __future__ import annotations

from typing import Any, Iterable, List


def _node_value(node: Any, key: str, default: Any = None) -> Any:
    if isinstance(node, dict):
        return node.get(key, default)
    return getattr(node, key, default)


def flatten_asset_ids(nodes: Iterable[Any]) -> List[str]:
    """
    Recursively flatten a nested asset tree into a list of selected ids.
    Accepts dicts or Pydantic models with id/selected/children fields.
    """
    result: List[str] = []

    for node in nodes or []:
        if not node:
            continue

        node_id = _node_value(node, "id")
        selected = bool(_node_value(node, "selected", False))
        children = _node_value(node, "children", None)

        if selected and node_id:
            result.append(str(node_id))

        if children:
            result.extend(flatten_asset_ids(children))

    seen = set()
    deduped: List[str] = []
    for asset_id in result:
        if asset_id not in seen:
            seen.add(asset_id)
            deduped.append(asset_id)

    return deduped
