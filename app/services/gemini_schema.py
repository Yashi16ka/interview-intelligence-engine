from typing import Any


def flatten_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    definitions = schema.get("$defs", {})

    def resolve(value: Any) -> Any:
        if isinstance(value, list):
            return [resolve(item) for item in value]

        if not isinstance(value, dict):
            return value

        if "$ref" in value:
            ref = value["$ref"]
            prefix = "#/$defs/"

            if not ref.startswith(prefix):
                raise ValueError(
                    f"Unsupported schema reference: {ref}"
                )

            name = ref[len(prefix):]

            if name not in definitions:
                raise ValueError(
                    f"Unknown schema reference: {ref}"
                )

            return resolve(definitions[name])

        return {
            key: resolve(item)
            for key, item in value.items()
            if key != "$defs"
        }

    return resolve(schema)
