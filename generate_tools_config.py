import json
import requests

# This is the default local ngrok API URL to get active tunnels
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"

TOOL_CONFIG_TEMPLATE = "tool_config_template.json"
TOOL_CONFIG_OUTPUT = "tool_config.json"

def get_ngrok_url():
    response = requests.get(NGROK_API_URL)
    response.raise_for_status()  # Make sure request succeeded
    tunnels = response.json().get("tunnels", [])
    for tunnel in tunnels:
        if tunnel.get("proto") == "https":
            return tunnel.get("public_url")
    raise Exception("No HTTPS ngrok tunnel found.")

def generate_tool_config():
    base_url = get_ngrok_url()
    print(f"[✓] Using ngrok URL: {base_url}")

    with open(TOOL_CONFIG_TEMPLATE, "r") as f:
        config = json.load(f)

    # Update all relevant URLs with the current ngrok base URL
    config["target_link_uri"] = f"{base_url}/lti/launch"
    config["oidc_initiation_url"] = f"{base_url}/lti/login"
    config["public_jwk_url"] = f"{base_url}/keys"
    config["extensions"][0]["settings"]["placements"][0]["target_link_uri"] = f"{base_url}/lti/launch"

    with open(TOOL_CONFIG_OUTPUT, "w") as f:
        json.dump(config, f, indent=2)
    print(f"[✓] tool_config.json written successfully.")

if __name__ == "__main__":
    generate_tool_config()
