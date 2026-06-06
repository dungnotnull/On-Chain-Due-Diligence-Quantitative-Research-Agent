"""RPC client for reading on-chain state via JSON-RPC."""

from __future__ import annotations

import hashlib
from typing import Any

from chainlens.collectors.base import AsyncCollectorBase
from chainlens.config.settings import ChainConfig


class RPCClient(AsyncCollectorBase):
    """JSON-RPC client for reading contract state."""

    def __init__(self, chain_config: ChainConfig) -> None:
        super().__init__()
        self.rpc_url = chain_config.rpc_url
        self.chain_id = chain_config.chain_id

    async def _rpc_call(self, method: str, params: list[Any]) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        resp = await self._request("POST", self.rpc_url, json=payload)
        data: dict[str, Any] = resp.json()
        if "error" in data:
            raise RuntimeError(f"RPC error: {data['error']}")
        return data.get("result", "")

    async def get_code(self, address: str) -> str:
        """Get deployed bytecode. Empty string means no contract."""
        return await self._rpc_call("eth_getCode", [address, "latest"])

    async def get_storage_at(self, address: str, slot: str) -> str:
        """Read a storage slot at the given address."""
        return await self._rpc_call("eth_getStorageAt", [address, slot, "latest"])

    async def call_contract(
        self, to: str, data: str, block: str = "latest"
    ) -> str:
        """Execute eth_call with encoded function data."""
        tx = {"to": to, "data": data}
        return await self._rpc_call("eth_call", [tx, block])

    async def get_block_number(self) -> int:
        result = await self._rpc_call("eth_blockNumber", [])
        return int(result, 16)

    async def get_transaction_count(self, address: str) -> int:
        result = await self._rpc_call("eth_getTransactionCount", [address, "latest"])
        return int(result, 16)

    async def contract_exists(self, address: str) -> bool:
        code = await self.get_code(address)
        return len(code) > 2  # "0x" alone = no code

    def encode_function_call(self, fn_signature: str, params: list[str] | None = None) -> str:
        """Build minimal eth_call data from function signature.
        This is a placeholder — real ABI encoding would use eth_abi.
        """
        fn_selector_bytes = hashlib.sha256(fn_signature.encode()).digest()[:4]
        return "0x" + fn_selector_bytes.hex() + "".join(params or [])
