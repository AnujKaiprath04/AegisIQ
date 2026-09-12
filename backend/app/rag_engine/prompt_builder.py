from typing import List
from app.rag_engine.types import CompressedPassage


class RAGPromptBuilder:
    """Builds grounded, anti-hallucination prompt payloads with source identifiers."""

    @classmethod
    def build_rag_system_prompt(cls, persona: str = "CEO") -> str:
        return (
            f"You are the AegisIQ Enterprise AI Decision Copilot in {persona.upper()} operational mode.\n"
            "Your objective is to provide high-precision, executive-ready decision intelligence grounded strictly in the provided enterprise knowledge passages.\n\n"
            "CRITICAL OPERATIONAL RULES:\n"
            "1. Ground every claim directly in the provided [Source N] passages.\n"
            "2. Include inline citation markers (e.g., [1], [2]) referencing the source number.\n"
            "3. If the context does not contain sufficient verified information, explicitly state that it is not documented in platform records.\n"
            "4. Maintain professional executive formatting with bullet points and bold highlights.\n"
            "5. Avoid speculative or ungrounded statements."
        )

    @classmethod
    def build_context_block(cls, passages: List[CompressedPassage]) -> str:
        if not passages:
            return "No matching verified enterprise passages retrieved."

        blocks = []
        for idx, p in enumerate(passages):
            title = p.metadata.get("title", "Enterprise Document")
            dept = p.metadata.get("department", "Executive")
            blocks.append(f"[Source {idx + 1}: {title} (Dept: {dept})]\n{p.content}")

        return "\n\n---\n\n".join(blocks)
