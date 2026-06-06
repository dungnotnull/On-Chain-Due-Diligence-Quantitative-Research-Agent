"""Explorer/Etherscan API client for verified source and contract metadata."""

from __future__ import annotations

from typing import Any

from chainlens.collectors.base import AsyncCollectorBase
from chainlens.config.settings import ChainConfig


class ExplorerClient(AsyncCollectorBase):
    """Fetch verified source, ABI, and contract metadata from block explorer APIs."""

    def __init__(self, chain_config: ChainConfig) -> None:
        super().__init__()
        self.api_url = chain_config.explorer_api_url
        self.api_key = chain_config.explorer_api_key

    async def _explorer_call(
        self, module: str, action: str, **params: str
    ) -> list[dict[str, Any]]:
        query = {
            "module": module,
            "action": action,
            "apikey": self.api_key,
            **params,
        }
        resp = await self._request("GET", self.api_url, params=query)
        data: dict[str, Any] = resp.json()
        if data.get("status") != "1":
            return []
        return data.get("result", [])

    async def get_verified_source(self, address: str) -> dict[str, Any]:
        """Get verified source code, ABI, compiler version."""
        results = await self._explorer_call(
            "contract", "getsourcecode", address=address
        )
        if not results:
            return {"verified": False, "source_code": "", "abi": ""}

        entry = results[0]
        return {
            "verified": entry.get("SourceCode") != "",
            "source_code": entry.get("SourceCode", ""),
            "abi": entry.get("ABI", "[]"),
            "compiler_version": entry.get("CompilerVersion", ""),
            "optimization_used": entry.get("OptimizationUsed", "0") == "1",
            "contract_name": entry.get("ContractName", ""),
        }

    async def get_abi(self, address: str) -> list[dict[str, Any]]:
        result = await self._explorer_call("contract", "getabi", address=address)
        if not result:
            return []
        return result if isinstance(result, list) else []

    async def get_contract_creation(self, address: str) -> str | None:
        """Get contract creation timestamp. Returns ISO string or None."""
        results = await self._explorer_call(
            "contract", "getcontractcreation", contractaddresses=address
        )
        if not results:
            return None
        return results[0].get("txHash")

    async def get_token_holders(
        self, address: str, limit: int = 1000
    ) -> list[dict[str, str]]:
        results = await self._explorer_call(
            "token",
            "tokenholderlist",
            contractaddress=address,
            limit=str(limit),
        )
        return results if isinstance(results, list) else []

    async def get_transaction_list(
        self, address: str, start_block: int = 0, end_block: int = 99999999
    ) -> list[dict[str, Any]]:
        results = await self._explorer_call(
            "account",
            "txlist",
            address=address,
            startblock=str(start_block),
            endblock=str(end_block),
            sort="desc",
        )
        return results if isinstance(results, list) else []
