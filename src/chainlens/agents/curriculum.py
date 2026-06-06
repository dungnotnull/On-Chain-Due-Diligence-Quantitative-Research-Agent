"""Curriculum — topic-to-explanation mapping with levels and real examples."""

from __future__ import annotations

from typing import Any

CURRICULUM: dict[str, dict[str, Any]] = {
    "erc20-approvals": {
        "title": "ERC-20 Approvals",
        "description": "How token approvals work, why they exist, and the risks",
        "beginner": {
            "explanation": (
                "An ERC-20 approval lets another address spend your tokens. "
                "When you call approve(spender, amount), you give that spender "
                "permission to transfer up to 'amount' tokens from your wallet. "
                "This is how DEXs like Uniswap can swap tokens on your behalf."
            ),
            "sections": [
                {
                    "title": "The Basics",
                    "content": (
                        "When you interact with a DEX or dApp, you first approve "
                        "the contract to spend your tokens. Without this step, the "
                        "contract cannot move your tokens. Think of it like pre-authorizing "
                        "a payment.\n\n"
                        "The approve() function takes two parameters:\n"
                        "- **spender**: the contract address that gets permission\n"
                        "- **amount**: the maximum number of tokens it can spend"
                    ),
                    "example": "approve(0xUniswapRouter, 1000 USDC) lets Uniswap spend 1000 USDC.",
                },
                {
                    "title": "Unlimited Approvals",
                    "content": (
                        "Many dApps ask for max uint256 approval — essentially "
                        "unlimited permission. This is convenient (no repeated approvals) "
                        "but risky: if the dApp contract is compromised, attackers "
                        "can drain your entire token balance."
                    ),
                    "example": "2^256-1 = infinite. Better: approve exact amounts.",
                },
                {
                    "title": "The Permit Pattern (EIP-2612)",
                    "content": (
                        "EIP-2612 introduces permit() — a gasless approval. Users "
                        "sign an off-chain message, and anyone can submit it on-chain. "
                        "This enables single-transaction swaps instead of approve-then-swap."
                    ),
                },
            ],
            "takeaways": [
                "Always check what approval amount you're signing for.",
                "Use exact amounts, not unlimited, when possible.",
                "Revoke approvals to contracts you no longer use.",
                "The permit() pattern saves gas and improves UX.",
            ],
        },
        "advanced": {
            "explanation": (
                "ERC-20 approvals are a critical security primitive. "
                "The approval mechanism creates a Allowance mapping that "
                "the spender can draw from via transferFrom(). Understanding "
                "the race condition between approve() and transferFrom() is "
                "essential for security analysis."
            ),
            "sections": [
                {
                    "title": "The Race Condition (Frontrunning)",
                    "content": (
                        "Changing an approval from X to Y creates a race window. "
                        "If the spender observes the tx that sets approval to Y, "
                        "they can frontrun it by spending X, then spend Y as well. "
                        "Mitigation: first set approval to 0, then to the new value."
                    ),
                    "example": "approve(c, 100) then approve(c, 50) — attacker can spend 150 total.",
                },
                {
                    "title": "Permit and EIP-2612",
                    "content": "Deep dive into EIP-2612: off-chain signing that eliminates the race condition.",
                    "example": "permit(owner, spender, value, deadline, v, r, s) is a gasless approve().",
                },
            ],
            "takeaways": [
                "Always use safeApprove or the 0-first pattern when changing approvals.",
                "EIP-2612 permit eliminates approve race conditions.",
                "Monitor approval events for suspicious patterns.",
            ],
        },
    },
    "impermanent-loss": {
        "title": "Impermanent Loss",
        "description": "How liquidity providers lose value relative to holding",
        "beginner": {
            "explanation": (
                "Impermanent loss (IL) happens when you provide liquidity to an AMM "
                "like Uniswap. If the price of your deposited tokens changes relative "
                "to each other, you end up with less value than if you'd just held them. "
                "It's called 'impermanent' because it reverses if prices return to "
                "their original ratio."
            ),
            "sections": [
                {
                    "title": "How It Works",
                    "content": (
                        "In a constant product AMM (x * y = k), when one token's "
                        "market price changes, arbitrageurs trade against the pool "
                        "until the pool price matches the market. This leaves you with "
                        "more of the cheaper token and less of the expensive one."
                    ),
                    "example": "You deposit 1 ETH + 3000 USDC (50/50). ETH doubles to $6000. "
                               "Arbitrage removes ETH until pool is balanced at the new price. "
                               "You end up with ~0.7 ETH + ~4242 USDC = $8442 vs $9000 if you held.",
                },
                {
                    "title": "IL Formula",
                    "content": (
                        "IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1\n\n"
                        "For a 2x price change: IL ≈ 5.7%\n"
                        "For a 3x price change: IL ≈ 13.4%\n"
                        "For a 10x price change: IL ≈ 43.7%"
                    ),
                },
            ],
            "takeaways": [
                "Impermanent loss is not actually permanent — it resolves if prices return.",
                "You still earn fees which can offset IL.",
                "Stablecoin pairs have minimal IL since prices barely change.",
            ],
        },
    },
    "honeypot": {
        "title": "Honeypot Tokens",
        "description": "Tokens designed to trap buyers who cannot sell",
        "beginner": {
            "explanation": (
                "A honeypot token is a scam token that lets you buy but prevents "
                "you from selling. The contract has a hidden check — usually in the "
                "transfer() or transferFrom() function — that reverts for everyone "
                "except the owner. Buyers are left holding worthless tokens."
            ),
            "sections": [
                {
                    "title": "Common Honeypot Patterns",
                    "content": (
                        "1. **Blacklisted seller**: transfer() reverts if caller is not "
                        "on an allowlist\n"
                        "2. **Tax manipulation**: buy tax is 0%, sell tax is 99%\n"
                        "3. **Max sell limit**: can only sell a tiny fraction of your "
                        "holdings per transaction\n"
                        "4. **Transfer cooldown**: can only sell after a cooldown that "
                        "never expires"
                    ),
                },
                {
                    "title": "How to Detect",
                    "content": (
                        "Simulate a buy and sell with a small amount in a forked chain "
                        "environment. If buy succeeds but sell reverts, it's a honeypot. "
                        "Also check: is the source verified? Are there owner-only transfer "
                        "functions? Is there a max-sell-amount variable?"
                    ),
                },
            ],
            "takeaways": [
                "Always verify you can sell a small test amount first.",
                "Check if the contract source is verified on Etherscan.",
                "Look for transfer-tax functions and max-sell-amount limits.",
                "If it sounds too good to be true, it probably is.",
            ],
        },
    },
}


def get_curriculum(topic: str, level: str = "beginner") -> dict[str, Any]:
    """Get curriculum entry for a topic at a given level."""
    normalized = topic.lower().replace(" ", "-").replace("_", "-")
    entry = CURRICULUM.get(normalized)
    if entry is None:
        return {
            "title": topic,
            "explanation": f"No detailed curriculum exists for '{topic}' yet.",
            "sections": [],
            "takeaways": [],
        }
    level_data = entry.get(level, entry.get("beginner", {}))
    return {
        "title": entry["title"],
        "explanation": level_data.get("explanation", ""),
        "sections": level_data.get("sections", []),
        "takeaways": level_data.get("takeaways", []),
    }
