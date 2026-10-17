#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
import urllib3


# ============================================================
# CONFIGURACIÓN
# ============================================================

# URL de la consola SentinelOne
S1_URL = "https://XXX.sentinelone.net"

# Token API de SentinelOne
S1_API_TOKEN = "TU_TOKEN_AQUI"

# Endpoint SDL/LRQ
QUERY_ENDPOINT = "/sdl/v2/api/queries"

# Intervalo entre comprobaciones de estado, en segundos
POLL_INTERVAL = 1

# Tiempo máximo de espera de una consulta
MAX_WAIT_SECONDS = 120

# Número máximo de resultados
RESULT_LIMIT = 10

# Verificación del certificado TLS
VERIFY_TLS = True


# ============================================================
# UTILIDADES
# ============================================================

def log(message):
    print(f"[INFO] {message}")


def debug(message, enabled=False):
    if enabled:
        print(f"[DEBUG] {message}")


def utc_iso(dt):
    """Convierte una fecha a formato ISO 8601 UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    dt = dt.astimezone(timezone.utc)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def enforce_limit(query):
    """
    Garantiza que la consulta termine con un límite
    máximo de RESULT_LIMIT resultados.
    """
    query = query.strip()

    if not query:
        raise ValueError("La consulta no puede estar vacía.")

    # Elimina un limit numérico que aparezca al final.
    query = re.sub(
        r"\|\s*limit\s+\d+\s*$",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()

    return f"{query} | limit {RESULT_LIMIT}"


def timestamp_to_string(value):
    """
    Convierte timestamps Unix en segundos, milisegundos,
    microsegundos o nanosegundos a una fecha UTC legible.
    """
    if value is None:
        return ""

    try:
        timestamp = float(value)

        if timestamp > 1e17:
            timestamp /= 1e9
        elif timestamp > 1e14:
            timestamp /= 1e6
        elif timestamp > 1e11:
            timestamp /= 1e3

        dt = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    except (ValueError, TypeError, OverflowError, OSError):
        return str(value)


# ============================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================

def validate_config():
    """Comprueba que la URL y el token estén configurados."""

    if not S1_URL or "XXX" in S1_URL:
        raise ValueError(
            "Configura la URL real de SentinelOne en S1_URL."
        )

    if (
        not S1_API_TOKEN
        or S1_API_TOKEN == "TU_TOKEN_AQUI"
    ):
        raise ValueError(
            "Configura el token en la variable S1_API_TOKEN."
        )


# ============================================================
# ARGUMENTOS
# ============================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta consultas PowerQuery en SentinelOne "
            "SDL/LRQ."
        )
    )

    parser.add_argument(
        "--query",
        required=True,
        help="Consulta PowerQuery que se ejecutará.",
    )

    parser.add_argument(
        "--hours",
        type=float,
        default=1,
        help=(
            "Número de horas hacia atrás. "
            "Por defecto: 1."
        ),
    )

    parser.add_argument(
        "--scope",
        default=None,
        help="Valor opcional para la cabecera S1-Scope.",
    )

    parser.add_argument(
        "--insecure",
        action="store_true",
        help=(
            "Desactiva la verificación TLS para esta ejecución. "
            "No recomendado en producción."
        ),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activa los mensajes de depuración.",
    )

    args = parser.parse_args()

    if args.hours <= 0:
        parser.error("--hours debe ser mayor que cero.")

    return args


# ============================================================
# SESIÓN HTTP
# ============================================================

def create_session(token, scope=None, verify_tls=True):
    """Crea una sesión HTTP autenticada."""

    session = requests.Session()

    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })

    if scope:
        session.headers["S1-Scope"] = scope

    session.verify = verify_tls

    if not verify_tls:
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

    return session


# ============================================================
# LANZAMIENTO DE CONSULTA
# ============================================================

def launch_query(
    session,
    base_url,
    query,
    start_time,
    end_time,
    debug_enabled=False,
):
    """Envía una consulta PowerQuery a SDL/LRQ."""

    endpoint = f"{base_url}{QUERY_ENDPOINT}"
    final_query = enforce_limit(query)

    body = {
        "queryType": "PQ",
        "tenant": True,
        "startTime": utc_iso(start_time),
        "endTime": utc_iso(end_time),
        "queryPriority": "HIGH",
        "pq": {
            "query": final_query,
            "resultType": "TABLE",
        },
    }

    log("Enviando consulta a SentinelOne SDL/LRQ.")
    log(f"Inicio UTC: {utc_iso(start_time)}")
    log(f"Fin UTC:    {utc_iso(end_time)}")
    log(f"Límite:     {RESULT_LIMIT} resultados")

    debug(f"Consulta: {final_query}", debug_enabled)

    response = session.post(
        endpoint,
        json=body,
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"Error al iniciar la consulta "
            f"(HTTP {response.status_code}): "
            f"{response.text}"
        )

    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "La API devolvió una respuesta que no es JSON."
        ) from exc

    debug(
        f"Respuesta inicial: {json.dumps(result, indent=2)}",
        debug_enabled,
    )

    query_id = result.get("id")

    if not query_id:
        raise RuntimeError(
            "La respuesta de SentinelOne no contiene "
            "el ID de la consulta."
        )

    forward_tag = response.headers.get(
        "X-Dataset-Query-Forward-Tag"
    )

    log(f"Consulta iniciada. ID: {query_id}")

    return query_id, forward_tag, result


# ============================================================
# SEGUIMIENTO DE CONSULTA
# ============================================================

def poll_query(
    session,
    base_url,
    query_id,
    forward_tag=None,
    initial_result=None,
    debug_enabled=False,
):
    """Espera hasta que la consulta haya terminado."""

    endpoint = f"{base_url}{QUERY_ENDPOINT}/{query_id}"

    headers = {}

    if forward_tag:
        headers["X-Dataset-Query-Forward-Tag"] = forward_tag

    last_step_seen = -1
    last_result = initial_result or {}
    start_wait = time.monotonic()

    while True:
        elapsed = time.monotonic() - start_wait

        if elapsed > MAX_WAIT_SECONDS:
            raise TimeoutError(
                f"La consulta superó el límite de "
                f"{MAX_WAIT_SECONDS} segundos."
            )

        response = session.get(
            endpoint,
            params={"lastStepSeen": last_step_seen},
            headers=headers,
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"Error consultando el estado "
                f"(HTTP {response.status_code}): "
                f"{response.text}"
            )

        try:
            result = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "La respuesta de estado no es JSON."
            ) from exc

        last_result = result

        debug(
            f"Estado: {json.dumps(result, indent=2)}",
            debug_enabled,
        )

        try:
            steps_completed = int(
                result.get("stepsCompleted", 0) or 0
            )
            steps_total = int(
                result.get("stepsTotal", 0) or 0
            )
        except (ValueError, TypeError):
            steps_completed = 0
            steps_total = 0

        log(
            f"Progreso: {steps_completed}/{steps_total} pasos"
        )

        if steps_completed > last_step_seen:
            last_step_seen = steps_completed

        status = str(
            result.get("status", "")
        ).upper()

        if status in {
            "FAILED",
            "ERROR",
            "CANCELLED",
            "CANCELED",
        }:
            raise RuntimeError(
                f"La consulta terminó con estado {status}: "
                f"{json.dumps(result)}"
            )

        if (
            steps_total > 0
            and steps_completed >= steps_total
        ):
            log("La consulta ha finalizado.")
            return last_result

        time.sleep(POLL_INTERVAL)


# ============================================================
# PRESENTACIÓN DE RESULTADOS
# ============================================================

def display_results(result):
    """Muestra las primeras filas de la consulta."""

    print("\n" + "=" * 80)
    print("RESULTADOS DE SENTINELONE")
    print("=" * 80)

    data = result.get("data", {})

    if not isinstance(data, dict):
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    columns = data.get("columns", [])
    values = data.get("values", [])

    if not values:
        print("La consulta no ha devuelto resultados.")
        return

    column_names = []

    for column in columns:
        if isinstance(column, dict):
            column_names.append(
                column.get("name")
                or column.get("field")
                or column.get("column")
                or str(column)
            )
        else:
            column_names.append(str(column))

    print(f"Resultados recibidos: {len(values)}")
    print(f"Máximo mostrado:      {RESULT_LIMIT}")

    for index, row in enumerate(
        values[:RESULT_LIMIT],
        start=1,
    ):
        print("\n" + "-" * 80)
        print(f"Resultado #{index}")
        print("-" * 80)

        if isinstance(row, dict):
            for key, value in row.items():
                if key.lower() == "timestamp":
                    value = timestamp_to_string(value)

                print(f"{key}: {value}")

        elif isinstance(row, (list, tuple)):
            for column_index, value in enumerate(row):
                if column_index < len(column_names):
                    name = column_names[column_index]
                else:
                    name = f"column_{column_index}"

                if name.lower() == "timestamp":
                    value = timestamp_to_string(value)

                print(f"{name}: {value}")

        else:
            print(row)

    if len(values) > RESULT_LIMIT:
        print(
            f"\nSe muestran únicamente los primeros "
            f"{RESULT_LIMIT} resultados."
        )


# ============================================================
# LIMPIEZA
# ============================================================

def cleanup_query(
    session,
    base_url,
    query_id,
    forward_tag=None,
    debug_enabled=False,
):
    """Intenta eliminar la consulta después de ejecutarla."""

    endpoint = f"{base_url}{QUERY_ENDPOINT}/{query_id}"

    headers = {}

    if forward_tag:
        headers["X-Dataset-Query-Forward-Tag"] = forward_tag

    try:
        response = session.delete(
            endpoint,
            headers=headers,
            timeout=30,
        )

        if response.ok:
            log("Limpieza de la consulta completada.")
        else:
            debug(
                f"No se pudo limpiar la consulta. "
                f"HTTP {response.status_code}: {response.text}",
                debug_enabled,
            )

    except requests.RequestException as exc:
        debug(
            f"Error durante la limpieza: {exc}",
            debug_enabled,
        )


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_arguments()

    query_id = None
    forward_tag = None
    session = None
    base_url = S1_URL.rstrip("/")

    try:
        validate_config()

        session = create_session(
            token=S1_API_TOKEN,
            scope=args.scope,
            verify_tls=(
                False if args.insecure else VERIFY_TLS
            ),
        )

        end_time = datetime.now(timezone.utc)

        start_time = end_time - timedelta(
            hours=args.hours
        )

        query_id, forward_tag, initial_result = launch_query(
            session=session,
            base_url=base_url,
            query=args.query,
            start_time=start_time,
            end_time=end_time,
            debug_enabled=args.debug,
        )

        result = poll_query(
            session=session,
            base_url=base_url,
            query_id=query_id,
            forward_tag=forward_tag,
            initial_result=initial_result,
            debug_enabled=args.debug,
        )

        display_results(result)

    except KeyboardInterrupt:
        print(
            "\n[AVISO] Ejecución interrumpida por el usuario.",
            file=sys.stderr,
        )
        return 130

    except (
        requests.RequestException,
        RuntimeError,
        TimeoutError,
        ValueError,
    ) as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1

    finally:
        if session is not None and query_id is not None:
            cleanup_query(
                session=session,
                base_url=base_url,
                query_id=query_id,
                forward_tag=forward_tag,
                debug_enabled=args.debug,
            )

        if session is not None:
            session.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
