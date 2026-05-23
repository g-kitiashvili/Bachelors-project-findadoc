from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from urllib.parse import urlsplit

import psycopg
import structlog

from pipeline.core.taxonomy import normalize_alias

log = structlog.get_logger("pipeline.deduplicator")


@dataclass(frozen=True)
class DedupStats:
    doctors_total: int
    doctors_merged: int
    doctors_flagged: int
    clinics_total: int
    clinics_merged: int
    clinics_flagged: int


class DedupRegression(RuntimeError):
    def __init__(self, kind: str, merged: int, total: int, fraction: float) -> None:
        super().__init__(f"dedup {kind} merge fraction {merged}/{total} exceeds {fraction}")


class _DSU:
    def __init__(self) -> None:
        self._p: dict[int, int] = {}

    def find(self, x: int) -> int:
        self._p.setdefault(x, x)
        while self._p[x] != x:
            self._p[x] = self._p[self._p[x]]
            x = self._p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._p[ra] = rb

    def groups(self) -> dict[int, list[int]]:
        out: dict[int, list[int]] = defaultdict(list)
        for x in self._p:
            out[self.find(x)].append(x)
        return out


def _source(url: str | None) -> str:
    return urlsplit(url or "").netloc


class Deduplicator:
    def __init__(self, dsn: str, *, max_merge_fraction: float = 0.8) -> None:
        self._dsn = dsn
        self._max = max_merge_fraction

    def run(self) -> DedupStats:
        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            self._reset(cur)
            d_total, d_merged, d_flagged = self._dedupe_doctors(cur)
            if d_total and d_merged / d_total > self._max:
                raise DedupRegression("doctor", d_merged, d_total, self._max)
            c_total, c_merged, c_flagged = self._dedupe_clinics(cur)
            if c_total and c_merged / c_total > self._max:
                raise DedupRegression("clinic", c_merged, c_total, self._max)
            conn.commit()
        stats = DedupStats(d_total, d_merged, d_flagged, c_total, c_merged, c_flagged)
        log.info("dedup_complete", **stats.__dict__)
        return stats

    def _reset(self, cur: psycopg.Cursor) -> None:
        cur.execute("DELETE FROM doctor_clinic WHERE via_merge")
        cur.execute("DELETE FROM doctor_specialty WHERE via_merge")
        cur.execute("UPDATE doctor SET status='ACTIVE', merged_into_id=NULL WHERE status='MERGED'")
        cur.execute("UPDATE clinic SET status='ACTIVE', merged_into_id=NULL WHERE status='MERGED'")

    def _dedupe_doctors(self, cur: psycopg.Cursor) -> tuple[int, int, int]:
        cur.execute(
            "SELECT id, full_name_en, full_name_ka, last_source_url, photo_url, "
            "(bio_en IS NOT NULL OR bio_ka IS NOT NULL), location_id "
            "FROM doctor WHERE status='ACTIVE'"
        )
        rows = cur.fetchall()
        total = len(rows)
        meta: dict[int, dict] = {}
        for did, nen, nka, url, photo, has_bio, loc in rows:
            meta[did] = {
                "en": normalize_alias(nen or ""), "ka": normalize_alias(nka or ""),
                "src": _source(url), "photo": bool(photo), "bio": bool(has_bio),
                "loc": loc, "specs": set(), "clinics": 0,
            }
        cur.execute(
            "SELECT ds.doctor_id, ds.specialty_id FROM doctor_specialty ds "
            "JOIN doctor d ON d.id=ds.doctor_id WHERE d.status='ACTIVE'"
        )
        for did, sid in cur.fetchall():
            if did in meta:
                meta[did]["specs"].add(sid)
        cur.execute(
            "SELECT dc.doctor_id, count(*) FROM doctor_clinic dc "
            "JOIN doctor d ON d.id=dc.doctor_id WHERE d.status='ACTIVE' GROUP BY dc.doctor_id"
        )
        for did, n in cur.fetchall():
            if did in meta:
                meta[did]["clinics"] = n

        name_dsu = _DSU()
        for did in meta:
            name_dsu.find(did)
        for key in ("en", "ka"):
            buckets: dict[str, list[int]] = defaultdict(list)
            for did, m in meta.items():
                if m[key]:
                    buckets[m[key]].append(did)
            for ids in buckets.values():
                for other in ids[1:]:
                    name_dsu.union(ids[0], other)

        merged = flagged = 0
        for ids in name_dsu.groups().values():
            if len(ids) < 2:
                continue
            spec_dsu = _DSU()
            for i in ids:
                spec_dsu.find(i)
            for a in range(len(ids)):
                for b in range(a + 1, len(ids)):
                    if meta[ids[a]]["specs"] & meta[ids[b]]["specs"]:
                        spec_dsu.union(ids[a], ids[b])
            for sub in spec_dsu.groups().values():
                if len(sub) < 2:
                    continue
                merged += self._merge_doctor_cluster(cur, sub, meta)
        return total, merged, flagged

    def _merge_doctor_cluster(self, cur: psycopg.Cursor, ids: list[int], meta: dict) -> int:
        canonical = max(ids, key=lambda i: (
            meta[i]["photo"] + meta[i]["bio"] + len(meta[i]["specs"]) + meta[i]["clinics"], -i,
        ))
        merged = 0
        for member in ids:
            if member == canonical:
                continue
            cur.execute(
                "INSERT INTO doctor_clinic (doctor_id, clinic_id, via_merge) "
                "SELECT %s, clinic_id, TRUE FROM doctor_clinic WHERE doctor_id=%s "
                "ON CONFLICT (doctor_id, clinic_id) DO NOTHING",
                (canonical, member),
            )
            cur.execute(
                "INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary, via_merge) "
                "SELECT %s, specialty_id, FALSE, TRUE FROM doctor_specialty WHERE doctor_id=%s "
                "ON CONFLICT (doctor_id, specialty_id) DO NOTHING",
                (canonical, member),
            )
            cur.execute(
                "UPDATE doctor SET location_id=%s WHERE id=%s AND location_id IS NULL",
                (meta[member]["loc"], canonical),
            )
            cur.execute(
                "UPDATE doctor SET status='MERGED', merged_into_id=%s WHERE id=%s",
                (canonical, member),
            )
            merged += 1
        return merged

    def _dedupe_clinics(self, cur: psycopg.Cursor) -> tuple[int, int, int]:
        cur.execute(
            "SELECT id, name_en, name_ka, last_source_url, phone, website, address "
            "FROM clinic WHERE status='ACTIVE'"
        )
        rows = cur.fetchall()
        total = len(rows)
        meta: dict[int, dict] = {}
        for cid, nen, nka, url, phone, website, address in rows:
            meta[cid] = {
                "en": normalize_alias(nen or ""), "ka": normalize_alias(nka or ""),
                "src": _source(url), "phone": normalize_alias(phone or ""),
                "web": normalize_alias(website or ""),
                "complete": bool(address) + bool(phone) + bool(website),
            }
        name_dsu = _DSU()
        for cid in meta:
            name_dsu.find(cid)
        for key in ("en", "ka"):
            buckets: dict[str, list[int]] = defaultdict(list)
            for cid, m in meta.items():
                if m[key]:
                    buckets[m[key]].append(cid)
            for ids in buckets.values():
                for other in ids[1:]:
                    name_dsu.union(ids[0], other)

        merged = flagged = 0
        for ids in name_dsu.groups().values():
            if len(ids) < 2:
                continue
            srcs = [meta[i]["src"] for i in ids]
            if len(set(srcs)) < len(srcs):
                flagged += 1
                log.warning("dedup_flagged", kind="clinic", ids=ids, name=meta[ids[0]]["en"])
                continue
            corr = _DSU()
            for i in ids:
                corr.find(i)
            for a in range(len(ids)):
                for b in range(a + 1, len(ids)):
                    ma, mb = meta[ids[a]], meta[ids[b]]
                    if (ma["phone"] and ma["phone"] == mb["phone"]) or (ma["web"] and ma["web"] == mb["web"]):
                        corr.union(ids[a], ids[b])
            for sub in corr.groups().values():
                if len(sub) < 2:
                    continue
                merged += self._merge_clinic_cluster(cur, sub, meta)
        return total, merged, flagged

    def _merge_clinic_cluster(self, cur: psycopg.Cursor, ids: list[int], meta: dict) -> int:
        canonical = max(ids, key=lambda i: (meta[i]["complete"], -i))
        merged = 0
        for member in ids:
            if member == canonical:
                continue
            cur.execute(
                "INSERT INTO doctor_clinic (doctor_id, clinic_id, via_merge) "
                "SELECT doctor_id, %s, TRUE FROM doctor_clinic WHERE clinic_id=%s "
                "ON CONFLICT (doctor_id, clinic_id) DO NOTHING",
                (canonical, member),
            )
            cur.execute(
                "UPDATE clinic SET status='MERGED', merged_into_id=%s WHERE id=%s",
                (canonical, member),
            )
            merged += 1
        return merged
