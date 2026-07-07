import json
import re


def repair_json(json_str: str) -> str:
    """
    Repair a truncated or incomplete JSON string by auto-closing
    open strings, brackets, and braces.
    """
    if not json_str:
        return json_str

    stack = []
    in_string = False
    escape = False
    repaired = []

    i = 0
    while i < len(json_str):
        char = json_str[i]
        if in_string:
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}':
                if stack and stack[-1] == '}':
                    stack.pop()
            elif char == ']':
                if stack and stack[-1] == ']':
                    stack.pop()

        repaired.append(char)
        i += 1

    if in_string:
        if escape:
            repaired.pop()
        repaired.append('"')

    while stack:
        close_char = stack.pop()
        repaired.append(close_char)

    return "".join(repaired)


def parse_llm_json(response: str) -> dict:
    """
    Parse JSON returned by an LLM.

    Handles:
    - ```json ... ``` code blocks
    - Extra whitespace
    - Text before/after the JSON object
    - Truncated or incomplete JSON structures via repair and backtracking
    """

    response = response.strip()

    # Remove markdown code fences
    response = re.sub(r"^```json", "", response, flags=re.IGNORECASE)
    response = re.sub(r"^```", "", response)
    response = re.sub(r"```$", "", response)
    response = response.strip()

    # Find the start of the first JSON object
    start = response.find("{")
    if start == -1:
        raise ValueError("No JSON object found in LLM response.")

    json_candidate = response[start:]

    current_str = json_candidate
    last_error = None

    for attempt in range(20):
        repaired = repair_json(current_str)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError as exc:
            last_error = exc
            pos = exc.pos
            # Truncate before the error position
            truncated = current_str[:pos].rstrip()

            # Strip trailing delimiters that would cause syntax error
            while truncated and truncated[-1] in (',', ':', '{', '[', ' ', '\n', '\r', '\t'):
                truncated = truncated[:-1].rstrip()

            if len(truncated) >= len(current_str):
                truncated = truncated[:-1].rstrip()

            if not truncated or truncated == current_str:
                break
            current_str = truncated

    print("\n========== INVALID JSON (Failed to parse or repair) ==========\n")
    print(response)
    print("\n==============================================================\n")
    raise ValueError(f"Failed to parse LLM JSON: {last_error}") from last_error