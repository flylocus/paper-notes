#!/usr/bin/env python3
"""
validate_structured_output.py — Schema-validated JSON 输出校验器

双角色设计：
  1. Sub-agent 侧：任务完成后自检，确保输出符合 schema 才返回
  2. Parent 侧：收到 delegate_task 结果后，解析并校验 JSON

用法：
  # Sub-agent 自检
  python3 validate_structured_output.py --check --data '{"name": "test"}' --schema '{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}'

  # Parent 提取 + 校验
  python3 validate_structured_output.py --extract --text "这里是一些思考...{\"name\":\"test\"}..." --schema '...'

Schema 格式：轻量 JSON Schema 子集
  {
    "type": "object",
    "properties": {
      "field_name": {
        "type": "string | number | boolean | array | object",
        "required": true/false,
        "items": {"type": "string"},          # 仅 array 类型
        "properties": {...}                     # 仅 object 类型
      }
    },
    "required": ["field_name"]                  # 顶层必填字段
  }
"""

import json, sys, re


# ── 类型检查器 ──────────────────────────────────────────────

PYTHON_TYPES = {
    "string": str,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def check_type(value, expected_type: str) -> tuple[bool, str]:
    """检查单个值的类型是否匹配。"""
    if expected_type == "number":
        return isinstance(value, (int, float)), f"期望 number, 得到 {type(value).__name__}"
    if expected_type == "null":
        return value is None, f"期望 null, 得到 {type(value).__name__}"
    py_type = PYTHON_TYPES.get(expected_type)
    if py_type is None:
        return True, f"未知类型约束 '{expected_type}'，跳过"
    return isinstance(value, py_type), f"期望 {expected_type}, 得到 {type(value).__name__}"


def validate_value(value, schema: dict, path: str = "$") -> list[str]:
    """
    递归校验单个值是否符合 schema 约束。
    返回错误信息列表（空=校验通过）。
    """
    errors = []

    if not isinstance(schema, dict):
        return errors

    expected_type = schema.get("type")

    if value is None:
        # null 值检查：如果类型本身是 null 则通过
        if expected_type == "null":
            return errors
        # 如果字段是 optional（required=false），null 也通过
        # 但如果 required=true 且为 null，由调用方检查
        return errors

    if expected_type and expected_type != "null":
        ok, msg = check_type(value, expected_type)
        if not ok:
            errors.append(f"{path}: {msg}")
            return errors  # 类型错了不再深入检查

    # 对象嵌套检查
    if expected_type == "object" and isinstance(value, dict):
        props = schema.get("properties", {})
        for prop_name, prop_schema in props.items():
            if prop_name in value:
                sub_errors = validate_value(
                    value[prop_name], prop_schema, f"{path}.{prop_name}"
                )
                errors.extend(sub_errors)
            else:
                # 属性级 required（boolean）检查
                if prop_schema.get("required", False):
                    errors.append(f"{path}.{prop_name}: 必填字段缺失")

        # 顶层 required（array）检查 — 仅顶层 schema 有
        top_required = schema.get("required")
        if isinstance(top_required, list):
            for req_name in top_required:
                if req_name not in value or value[req_name] is None:
                    errors.append(f"{path}.{req_name}: 必填字段缺失或为 null")

    # 数组嵌套检查
    if expected_type == "array" and isinstance(value, list):
        items_schema = schema.get("items", {})
        if items_schema:
            for i, item in enumerate(value):
                sub_errors = validate_value(item, items_schema, f"{path}[{i}]")
                errors.extend(sub_errors)

    return errors


# ── 从自然语言中提取 JSON ─────────────────────────────────

def extract_json(text: str) -> tuple[dict | None, str]:
    """
    从 sub-agent 的文本输出中提取第一个 JSON 对象。
    支持：
    - 纯 JSON（无多余文字）
    - ```json ... ``` 代码块
    - 含有前缀后缀的自然语言
    返回 (parsed_dict, raw_match) 或 (None, "")
    """
    # 先尝试代码块
    block_match = re.search(r"```(?:json)?\s*\n?(\{.*?\})\s*\n?```", text, re.DOTALL)
    if block_match:
        raw = block_match.group(1)
        try:
            return json.loads(raw), raw
        except json.JSONDecodeError:
            pass

    # 尝试直接 parse（纯 JSON）
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            return json.loads(stripped), stripped
        except json.JSONDecodeError:
            pass

    # 尝试找第一对 { ... }
    start = text.find("{")
    if start >= 0:
        # 暴力找匹配的闭合 }
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start:i+1]
                    try:
                        return json.loads(candidate), candidate
                    except json.JSONDecodeError:
                        # 如果最后一个}无法解析，继续找
                        pass
        # 最后的尝试：用最后一个 }
        last_brace = text.rfind("}")
        if last_brace > start:
            candidate = text[start:last_brace+1]
            try:
                return json.loads(candidate), candidate
            except json.JSONDecodeError:
                pass

    return None, ""


# ── 输出模板生成 ──────────────────────────────────────────

def build_output_instruction(schema: dict) -> str:
    """
    根据 schema 生成 sub-agent 输出指令（嵌入 context）。
    返回一段描述性文字，告诉 sub-agent 必须以 JSON 格式返回什么。
    """
    def _describe_prop(name, prop_schema, depth=0):
        indent = "  " * (depth + 1)
        ptype = prop_schema.get("type", "any")
        required = prop_schema.get("required", False)
        req_mark = "【必填】" if required else "【选填】"
        desc = prop_schema.get("description", "")
        desc_str = f" — {desc}" if desc else ""
        lines = [f"{indent}- `{name}` ({ptype}) {req_mark}{desc_str}"]

        if ptype == "object":
            sub_props = prop_schema.get("properties", {})
            for sub_name, sub_schema in sub_props.items():
                lines.extend(_describe_prop(sub_name, sub_schema, depth + 1))

        if ptype == "array":
            items = prop_schema.get("items", {})
            if items.get("type"):
                lines.append(f'{indent}  元素类型: {items["type"]}')

        return lines

    lines = [
        "你必须返回一个有效的 JSON 对象，不要包含 JSON 代码块标记（```），不要包含额外说明文字。",
        f"JSON 结构如下：",
    ]

    props = schema.get("properties", {})
    for name, prop_schema in props.items():
        lines.extend(_describe_prop(name, prop_schema))

    required = schema.get("required", [])
    if required:
        lines.append(f"")
        lines.append(f"必填字段: {', '.join(required)}")

    return "\n".join(lines)


# ── CLI 双模式 ─────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Structured output validator")
    parser.add_argument("--check", action="store_true",
                        help="校验模式：校验 JSON 数据是否符合 schema")
    parser.add_argument("--extract", action="store_true",
                        help="提取模式：从文本中提取 JSON 并校验")
    parser.add_argument("--data", help="JSON 数据（--check 模式）")
    parser.add_argument("--text", help="含 JSON 的文本（--extract 模式）")
    parser.add_argument("--schema", required=True, help="JSON schema 定义")
    parser.add_argument("--instruction", action="store_true",
                        help="仅输出 sub-agent 响应指令（基于 schema 生成）")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # 解析 schema
    try:
        schema = json.loads(args.schema)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "error": f"Schema 解析失败: {e}"}))
        sys.exit(1)

    # 指令生成模式
    if args.instruction:
        print(build_output_instruction(schema))
        sys.exit(0)

    # 校验模式
    if args.check:
        if not args.data:
            print(json.dumps({"valid": False, "error": "--check 模式需要 --data 参数"}))
            sys.exit(1)
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(json.dumps({"valid": False, "error": f"JSON 解析失败: {e}", "raw": args.data}))
            sys.exit(1)
        errors = validate_value(data, schema)
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "field_count": len(data) if isinstance(data, dict) else 0,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["valid"] else 1)

    # 提取模式
    if args.extract:
        if not args.text:
            print(json.dumps({"valid": False, "error": "--extract 模式需要 --text 参数"}))
            sys.exit(1)
        parsed, raw_match = extract_json(args.text)
        if parsed is None:
            print(json.dumps({"valid": False, "error": "未从文本中找到 JSON", "text_preview": args.text[:200]}))
            sys.exit(1)
        errors = validate_value(parsed, schema)
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "raw_length": len(raw_match),
            "field_count": len(parsed) if isinstance(parsed, dict) else 0,
            "parsed": parsed,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["valid"] else 1)

    # 无模式 -> 显示用法
    parser.print_help()


if __name__ == "__main__":
    main()
