import re
from typing import Any, Dict, List, Optional
from app.prompt_service.types import FewShotExample


class PromptFormatter:
    """Safely interpolates variables into parameterized prompt templates and formats few-shot examples."""

    @classmethod
    def interpolate(cls, template_text: str, variables: Dict[str, Any]) -> str:
        if not template_text:
            return ""

        rendered = template_text
        # Find all placeholders matching {{variable_name}}
        matches = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template_text)
        
        for var_name in matches:
            val = variables.get(var_name)
            placeholder = f"{{{{{var_name}}}}}"
            if val is not None:
                rendered = rendered.replace(placeholder, str(val))
            else:
                rendered = rendered.replace(placeholder, f"[{var_name}]")

        return rendered.strip()

    @classmethod
    def attach_few_shots(cls, rendered_text: str, examples: List[FewShotExample]) -> str:
        if not examples:
            return rendered_text

        blocks = ["\n\n### Few-Shot Reference Exemplars:"]
        for idx, ex in enumerate(examples):
            blocks.append(
                f"**Example {idx + 1}**:\n"
                f"- Input: {ex.user_input}\n"
                + (f"- Context: {ex.context}\n" if ex.context else "")
                + f"- Ideal Output: {ex.ideal_output}"
            )

        return rendered_text + "\n" + "\n\n".join(blocks)
