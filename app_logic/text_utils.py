def clean_text(value):
    if value is None:
        return ""

    try:
        if value != value:
            return ""
    except Exception:
        pass

    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def clean_mapping_values(source, keys):
    values = source or {}
    return {key: clean_text(values.get(key)) for key in keys}
