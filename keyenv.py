def get_api_key():
    import os
    api_key = os.environ.get("RECRUIT_API_KEY")

    if not api_key:
        keyfile = os.path.join(os.path.dirname(__file__), "./key.json")
        if os.path.isfile(keyfile):
            import json
            with open(keyfile, "r", encoding="utf-8") as f:
                key_json = json.load(f)
                api_key = key_json["api_key"]

    return api_key
