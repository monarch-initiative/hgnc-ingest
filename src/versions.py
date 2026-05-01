"""Upstream source version fetchers for hgnc-ingest.

URLs are read from download.yaml (single source of truth). Sources are split
by URL substring so the per-source URL grouping stays coherent.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import requests

from kozahub_metadata_schema.writer import urls_from_download_yaml


INGEST_DIR = Path(__file__).resolve().parents[1]
DOWNLOAD_YAML = INGEST_DIR / "download.yaml"


def _now_iso() -> str:
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _hgnc_version() -> tuple[str, str]:
    try:
        r = requests.get(
            "https://rest.genenames.org/info",
            headers={"Accept": "application/json"},
            timeout=10,
        )
        r.raise_for_status()
        last_modified = r.json().get("lastModified", "")
        return last_modified.split("T")[0] or "unknown", "rest_info_api"
    except Exception:
        return "unknown", "unavailable"


def _alliance_version() -> tuple[str, str]:
    try:
        r = requests.get(
            "https://fms.alliancegenome.org/api/releaseversion/current",
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["releaseVersion"], "alliance_fms_api"
    except Exception:
        return "unknown", "unavailable"


def get_source_versions() -> list[dict[str, Any]]:
    hgnc_urls = urls_from_download_yaml(DOWNLOAD_YAML, contains=["public-download-files/hgnc"])
    agr_urls = urls_from_download_yaml(DOWNLOAD_YAML, contains=["alliancegenome.org"])

    hgnc_ver, hgnc_method = _hgnc_version()
    agr_ver, agr_method = _alliance_version()
    now = _now_iso()
    return [
        {
            "id": "infores:hgnc",
            "name": "HUGO Gene Nomenclature Committee",
            "urls": hgnc_urls,
            "version": hgnc_ver,
            "version_method": hgnc_method,
            "retrieved_at": now,
        },
        {
            "id": "infores:agr",
            "name": "Alliance of Genome Resources",
            "urls": agr_urls,
            "version": agr_ver,
            "version_method": agr_method,
            "retrieved_at": now,
        },
    ]
