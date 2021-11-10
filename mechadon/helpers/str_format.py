def camel_to_snake(s: str) -> str:
    return ''.join([
        f'_{c.lower()}' if c.isupper() else c for c in s
    ]).lstrip('_')
