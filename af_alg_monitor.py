#!/usr/bin/env python3
"""
af_alg_monitor.py — Detector de socket(AF_ALG) en tiempo real
Lee /var/log/audit/audit.log buscando los valores RAW (sin interpretar).

ausearch -i muestra valores legibles (a0=alg, syscall=socket),
pero en el log crudo aparecen como números:
  syscall=41   (SYS_socket en x86_64)
  a0=26        (AF_ALG=38 en hex sin 0x)
  a1=5         (SOCK_SEQPACKET)

Requiere:
  auditctl -a always,exit -F arch=b64 -S socket -F a0=38 -k exploit_crypto
"""

import os
import signal
import sys
import time
from datetime import datetime

AUDIT_LOG = "/var/log/audit/audit.log"

# Valores RAW tal como aparecen en el log sin interpretar
# AF_ALG = 38 decimal = 0x26 hex → auditd lo escribe como "26"
AF_ALG_RAW        = "a0=26"
SOCK_SEQPACKET_RAW = "a1=8005"
SYSCALL_RAW        = "syscall=41"   # socket() en x86_64

# Por si auditd está configurado para escribir los nombres
AF_ALG_NAME        = "a0=alg"
SOCK_SEQPACKET_NAME = "a1=SOCK_SEQPACKET"
SYSCALL_NAME        = "syscall=socket"


def is_af_alg_socket(line):
    """Detecta socket(AF_ALG, SOCK_SEQPACKET) en formato raw o interpretado."""
    if "type=SYSCALL" not in line:
        return False

    has_syscall = SYSCALL_RAW in line or SYSCALL_NAME in line
    has_a0      = AF_ALG_RAW in line or AF_ALG_NAME in line
    has_a1      = SOCK_SEQPACKET_RAW in line or SOCK_SEQPACKET_NAME in line

    return has_syscall and has_a0 and has_a1


def parse_fields(line):
    fields = {}
    for token in line.split():
        if "=" in token:
            k, _, v = token.partition("=")
            fields[k] = v.strip("'\"")
    return fields


def format_alert(fields, raw_line):
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pid  = fields.get("pid",  "?")
    comm = fields.get("comm", "?")
    exe  = fields.get("exe",  "?")
    uid  = fields.get("uid",  "?")
    auid = fields.get("auid", "?")
    subj = fields.get("subj", "N/A")

    return (
        f"\n{'─'*64}\n"
        f"  🚨 socket(AF_ALG) detectado  [{ts}]\n"
        f"{'─'*64}\n"
        f"  PID     : {pid}\n"
        f"  Proceso : {comm}  ({exe})\n"
        f"  UID     : {uid}   AUID: {auid}\n"
        f"  SELinux : {subj}\n"
        f"  Raw     : {raw_line[:100].strip()}\n"
        f"{'─'*64}"
    )


def debug_mode(last_n=20):
    """Muestra las últimas N líneas del log para diagnóstico."""
    print(f"[DEBUG] Últimas {last_n} líneas de {AUDIT_LOG}:\n")
    try:
        with open(AUDIT_LOG, "r") as f:
            lines = f.readlines()
        for line in lines[-last_n:]:
            print(" ", line.rstrip())
    except PermissionError:
        print("[!] Sin permisos de lectura. Usa sudo.")
    print()


def run_detect(debug=False):
    if debug:
        debug_mode()
        print("[*] (Modo debug: muestra el log crudo para verificar formato)\n")

    print(f"[*] Monitorizando: {AUDIT_LOG}")
    print(f"[*] Buscando: syscall=41 (o socket) + a0=26 (o alg) + a1=5 (o SOCK_SEQPACKET)")
    print()

    if not os.path.exists(AUDIT_LOG):
        print(f"[!] {AUDIT_LOG} no existe. ¿auditd está corriendo?")
        sys.exit(1)

    signal.signal(signal.SIGINT, lambda s, f: (print("\n[*] Detenido."), sys.exit(0)))

    with open(AUDIT_LOG, "r") as f:
        f.seek(0, 2)
        print("[*] Esperando eventos (lanza el exploit en otro terminal)...\n")
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.05)
                continue
            #if is_af_alg_socket(line):
            fields = parse_fields(line)
            print(format_alert(fields, line))


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Detector de socket(AF_ALG) — Blue Team Tool",
        epilog=(
            "Ejemplos:\n"
            "  sudo python3 af_alg_monitor.py\n"
            "  sudo python3 af_alg_monitor.py --debug   # muestra log crudo para diagnóstico\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true",
                        help="Muestra las últimas líneas del log crudo antes de arrancar")
    args = parser.parse_args()

    if os.geteuid() != 0:
        print("[!] Requiere root.")
        sys.exit(1)

    print("=" * 64)
    print("  af_alg_monitor.py — Detector socket(AF_ALG)")
    print("  CopyFail/CopyFlag Blue Team Detection Tool")
    print("=" * 64 + "\n")

    run_detect(debug=args.debug)


if __name__ == "__main__":
    main()
