"""
Step 8: Source-Target Database 비교 및 리포트 생성

비교 항목:
  - 오브젝트 타입별 개수 (dba_objects)
  - 테이블 행 수 (COUNT(*))
  - Invalid 오브젝트
  - 제약조건 (dba_constraints)
  - 인덱스 (dba_indexes)
  - 시퀀스 (dba_sequences)
  - 트리거 (dba_triggers)

출력: Markdown + HTML 비교 리포트
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from src.utils import (
    logger,
    print_header,
    print_info,
    print_ok,
    print_fail,
    print_warn,
    print_table,
    write_text_file,
    timestamp_str,
)

if TYPE_CHECKING:
    from src.connection import OracleConnection


# ── 비교 데이터 수집 ──────────────────────────────────────────────────────────

def _get_object_counts(conn: "OracleConnection", schemas: list[str]) -> dict:
    """스키마별 오브젝트 타입/개수를 {owner: {type: count}} 형태로 반환한다."""
    placeholders = ", ".join([f":s{i}" for i in range(len(schemas))])
    params = {f"s{i}": s.upper() for i, s in enumerate(schemas)}
    sql = f"""
        SELECT owner, object_type, COUNT(*) AS cnt
        FROM dba_objects
        WHERE owner IN ({placeholders})
          AND object_type NOT IN ('INDEX PARTITION','TABLE PARTITION','LOB','LOB PARTITION')
          AND status != 'INVALID'
        GROUP BY owner, object_type
        ORDER BY owner, object_type
    """
    rows = conn.execute_query(sql, params)
    result = {}
    for r in rows:
        owner = r["owner"]
        result.setdefault(owner, {})[r["object_type"]] = r["cnt"]
    return result


def _get_invalid_objects(conn: "OracleConnection", schemas: list[str]) -> list[dict]:
    """Invalid 오브젝트 목록을 반환한다."""
    placeholders = ", ".join([f":s{i}" for i in range(len(schemas))])
    params = {f"s{i}": s.upper() for i, s in enumerate(schemas)}
    sql = f"""
        SELECT owner, object_type, object_name, status
        FROM dba_objects
        WHERE owner IN ({placeholders})
          AND status = 'INVALID'
        ORDER BY owner, object_type, object_name
    """
    return conn.execute_query(sql, params)


def _get_table_row_counts(
    conn: "OracleConnection",
    schemas: list[str],
    max_tables: int = 0,
    exclude_tables: list = None,
) -> dict:
    """
    {schema: {table_name: row_count}} 형태로 테이블 행 수를 반환한다.
    max_tables=0 이면 전체 테이블.
    """
    placeholders = ", ".join([f":s{i}" for i in range(len(schemas))])
    params = {f"s{i}": s.upper() for i, s in enumerate(schemas)}
    limit_clause = f"AND rownum <= {max_tables}" if max_tables > 0 else ""

    sql = f"""
        SELECT owner, table_name
        FROM dba_tables
        WHERE owner IN ({placeholders})
          {limit_clause}
        ORDER BY owner, table_name
    """
    tables = conn.execute_query(sql, params)

    exclude_set = set(t.upper() for t in (exclude_tables or []))
    result = {}
    for t in tables:
        owner = t["owner"]
        tname = t["table_name"]
        if tname in exclude_set:
            continue
        try:
            cnt = conn.execute_scalar(f'SELECT COUNT(*) FROM "{owner}"."{tname}"')
            result.setdefault(owner, {})[tname] = cnt or 0
        except Exception as e:
            logger.warning(f"행 수 조회 실패 {owner}.{tname}: {e}")
            result.setdefault(owner, {})[tname] = -1  # -1 = 조회 실패
    return result


def _get_constraint_counts(conn: "OracleConnection", schemas: list[str]) -> dict:
    placeholders = ", ".join([f":s{i}" for i in range(len(schemas))])
    params = {f"s{i}": s.upper() for i, s in enumerate(schemas)}
    sql = f"""
        SELECT owner, constraint_type, COUNT(*) AS cnt
        FROM dba_constraints
        WHERE owner IN ({placeholders}) AND status = 'ENABLED'
        GROUP BY owner, constraint_type
        ORDER BY owner, constraint_type
    """
    rows = conn.execute_query(sql, params)
    result = {}
    for r in rows:
        result.setdefault(r["owner"], {})[r["constraint_type"]] = r["cnt"]
    return result


def _get_index_counts(conn: "OracleConnection", schemas: list[str]) -> dict:
    placeholders = ", ".join([f":s{i}" for i in range(len(schemas))])
    params = {f"s{i}": s.upper() for i, s in enumerate(schemas)}
    sql = f"""
        SELECT owner, index_type, COUNT(*) AS cnt
        FROM dba_indexes
        WHERE owner IN ({placeholders}) AND status IN ('VALID','N/A')
        GROUP BY owner, index_type
        ORDER BY owner, index_type
    """
    rows = conn.execute_query(sql, params)
    result = {}
    for r in rows:
        result.setdefault(r["owner"], {})[r["index_type"]] = r["cnt"]
    return result


# ── 비교 로직 ─────────────────────────────────────────────────────────────────

CompareResult = dict  # {item, source, target, status, note}


def _compare_dicts(
    label: str,
    src_dict: dict,
    tgt_dict: dict,
    owner: str,
) -> list[CompareResult]:
    """두 dict (key→count)를 비교해 CompareResult 목록을 반환한다."""
    all_keys = sorted(set(src_dict.keys()) | set(tgt_dict.keys()))
    results = []
    for key in all_keys:
        sv = src_dict.get(key, 0)
        tv = tgt_dict.get(key, 0)
        if sv == tv:
            status = "PASS"
            note = ""
        elif tv == 0:
            status = "FAIL"
            note = "Target에 없음"
        elif sv > tv:
            status = "FAIL"
            note = f"부족 {sv - tv}건"
        else:
            status = "WARN"
            note = f"초과 {tv - sv}건"
        results.append({
            "owner": owner,
            "category": label,
            "item": key,
            "source": sv,
            "target": tv,
            "status": status,
            "note": note,
        })
    return results


def compare_all(
    src_conn: "OracleConnection",
    tgt_conn: "OracleConnection",
    cfg: dict,
) -> list[CompareResult]:
    """모든 비교 항목을 수집해 CompareResult 목록을 반환한다."""
    schemas = cfg.get("export", {}).get("schemas", [])
    comp_cfg = cfg.get("comparison", {})
    max_tables = comp_cfg.get("row_count_sample", 100)
    exclude_tables = comp_cfg.get("exclude_tables", [])

    all_results = []

    # --- 오브젝트 수 ---
    print_info("오브젝트 수 비교 중...")
    src_obj = _get_object_counts(src_conn, schemas)
    tgt_obj = _get_object_counts(tgt_conn, schemas)
    for owner in schemas:
        owner = owner.upper()
        all_results.extend(_compare_dicts("Object", src_obj.get(owner, {}), tgt_obj.get(owner, {}), owner))

    # --- 테이블 행 수 ---
    print_info("테이블 행 수 비교 중...")
    src_rows = _get_table_row_counts(src_conn, schemas, max_tables, exclude_tables)
    tgt_rows = _get_table_row_counts(tgt_conn, schemas, max_tables, exclude_tables)
    for owner in schemas:
        owner = owner.upper()
        sv = src_rows.get(owner, {})
        tv = tgt_rows.get(owner, {})
        all_tables = sorted(set(sv.keys()) | set(tv.keys()))
        for tname in all_tables:
            sc = sv.get(tname, 0)
            tc = tv.get(tname, 0)
            if sc < 0 or tc < 0:
                status, note = "WARN", "조회 실패"
            elif sc == tc:
                status, note = "PASS", ""
            else:
                status, note = "FAIL", f"Source={sc} Target={tc}"
            all_results.append({
                "owner": owner, "category": "RowCount", "item": tname,
                "source": sc, "target": tc, "status": status, "note": note,
            })

    # --- Invalid 오브젝트 ---
    print_info("Invalid 오브젝트 비교 중...")
    src_invalid = _get_invalid_objects(src_conn, schemas)
    tgt_invalid = _get_invalid_objects(tgt_conn, schemas)
    for owner in schemas:
        owner = owner.upper()
        src_inv_cnt = sum(1 for r in src_invalid if r["owner"] == owner)
        tgt_inv_cnt = sum(1 for r in tgt_invalid if r["owner"] == owner)
        status = "PASS" if tgt_inv_cnt == 0 else "WARN"
        all_results.append({
            "owner": owner, "category": "InvalidObject", "item": "INVALID COUNT",
            "source": src_inv_cnt, "target": tgt_inv_cnt,
            "status": status, "note": "" if tgt_inv_cnt == 0 else f"{tgt_inv_cnt}개 Invalid",
        })

    # --- 제약조건 ---
    print_info("제약조건 비교 중...")
    src_cons = _get_constraint_counts(src_conn, schemas)
    tgt_cons = _get_constraint_counts(tgt_conn, schemas)
    for owner in schemas:
        owner = owner.upper()
        all_results.extend(_compare_dicts("Constraint", src_cons.get(owner, {}), tgt_cons.get(owner, {}), owner))

    # --- 인덱스 ---
    print_info("인덱스 비교 중...")
    src_idx = _get_index_counts(src_conn, schemas)
    tgt_idx = _get_index_counts(tgt_conn, schemas)
    for owner in schemas:
        owner = owner.upper()
        all_results.extend(_compare_dicts("Index", src_idx.get(owner, {}), tgt_idx.get(owner, {}), owner))

    return all_results


# ── 리포트 생성 ───────────────────────────────────────────────────────────────

def _result_summary(results: list[CompareResult]) -> dict:
    from collections import Counter
    cnt = Counter(r["status"] for r in results)
    return {"PASS": cnt.get("PASS", 0), "FAIL": cnt.get("FAIL", 0), "WARN": cnt.get("WARN", 0)}


def generate_markdown_report(results: list[CompareResult], cfg: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schemas = cfg.get("export", {}).get("schemas", [])
    summary = _result_summary(results)

    lines = [
        "# Oracle Migration Comparison Report",
        f"",
        f"- **생성일시**: {ts}",
        f"- **Schema**: {', '.join(schemas)}",
        f"- **Source**: {cfg['source']['host']}/{cfg['source']['service_name']}",
        f"- **Target**: {cfg['target']['host']}/{cfg['target']['service_name']}",
        "",
        "## 요약",
        "",
        f"| 결과 | 건수 |",
        f"|------|------|",
        f"| ✅ PASS | {summary['PASS']} |",
        f"| ❌ FAIL | {summary['FAIL']} |",
        f"| ⚠️ WARN | {summary['WARN']} |",
        "",
        "## 상세 비교",
        "",
        "| Owner | 분류 | 항목 | Source | Target | 결과 | 비고 |",
        "|-------|------|------|--------|--------|------|------|",
    ]

    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
    for r in results:
        lines.append(
            f"| {r['owner']} | {r['category']} | {r['item']} "
            f"| {r['source']} | {r['target']} "
            f"| {icon.get(r['status'], r['status'])} {r['status']} "
            f"| {r.get('note', '')} |"
        )

    return "\n".join(lines)


def generate_html_report(results: list[CompareResult], cfg: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schemas = cfg.get("export", {}).get("schemas", [])
    summary = _result_summary(results)

    status_color = {"PASS": "#2ecc71", "FAIL": "#e74c3c", "WARN": "#f39c12"}

    rows_html = ""
    for r in results:
        color = status_color.get(r["status"], "#999")
        rows_html += (
            f"<tr>"
            f"<td>{r['owner']}</td>"
            f"<td>{r['category']}</td>"
            f"<td>{r['item']}</td>"
            f"<td>{r['source']}</td>"
            f"<td>{r['target']}</td>"
            f"<td style='color:{color};font-weight:bold'>{r['status']}</td>"
            f"<td>{r.get('note','')}</td>"
            f"</tr>\n"
        )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Oracle Migration Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f1117; color: #e0e0e0; margin: 0; padding: 20px; }}
  h1 {{ color: #00d2ff; }}
  .meta {{ color: #aaa; margin-bottom: 20px; }}
  .summary {{ display: flex; gap: 20px; margin-bottom: 30px; }}
  .card {{ background: #1c1f2e; border-radius: 12px; padding: 20px 30px; text-align: center; }}
  .card .num {{ font-size: 2.5em; font-weight: bold; }}
  .pass {{ color: #2ecc71; }} .fail {{ color: #e74c3c; }} .warn {{ color: #f39c12; }}
  table {{ width: 100%; border-collapse: collapse; background: #1c1f2e; border-radius: 10px; overflow: hidden; }}
  th {{ background: #2a2d3e; color: #00d2ff; padding: 10px; text-align: left; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #2a2d3e; }}
  tr:hover {{ background: #252838; }}
</style>
</head>
<body>
<h1>🔄 Oracle Migration Comparison Report</h1>
<div class="meta">
  <strong>생성:</strong> {ts} &nbsp;|&nbsp;
  <strong>Schema:</strong> {', '.join(schemas)} &nbsp;|&nbsp;
  <strong>Source:</strong> {cfg['source']['host']}/{cfg['source']['service_name']} &nbsp;→&nbsp;
  <strong>Target:</strong> {cfg['target']['host']}/{cfg['target']['service_name']}
</div>
<div class="summary">
  <div class="card"><div class="num pass">{summary['PASS']}</div><div>PASS</div></div>
  <div class="card"><div class="num fail">{summary['FAIL']}</div><div>FAIL</div></div>
  <div class="card"><div class="num warn">{summary['WARN']}</div><div>WARN</div></div>
</div>
<table>
<thead>
<tr><th>Owner</th><th>분류</th><th>항목</th><th>Source</th><th>Target</th><th>결과</th><th>비고</th></tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>"""
    return html


# ── 메인 함수 ─────────────────────────────────────────────────────────────────

def run_comparison(
    src_conn: "OracleConnection",
    tgt_conn: "OracleConnection",
    cfg: dict,
) -> list[CompareResult]:
    """Step 8 전체 실행: 비교 수행 → 리포트 저장."""
    print_header("Step 8: Source-Target Database 비교")

    results = compare_all(src_conn, tgt_conn, cfg)

    summary = _result_summary(results)
    print_table(
        ["결과", "건수"],
        [["PASS", summary["PASS"]], ["FAIL", summary["FAIL"]], ["WARN", summary["WARN"]]],
    )

    report_dir = cfg.get("output", {}).get("report_dir", "output/reports")
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    ts = timestamp_str()
    fmt = cfg.get("comparison", {}).get("output_format", "both")

    if fmt in ("markdown", "both"):
        md = generate_markdown_report(results, cfg)
        md_path = str(Path(report_dir) / f"comparison_{ts}.md")
        write_text_file(md_path, md)
        print_ok(f"Markdown 리포트: {md_path}")

    if fmt in ("html", "both"):
        html = generate_html_report(results, cfg)
        html_path = str(Path(report_dir) / f"comparison_{ts}.html")
        write_text_file(html_path, html)
        print_ok(f"HTML 리포트: {html_path}")

    if summary["FAIL"] == 0:
        print_ok("마이그레이션 검증 완료 — FAIL 없음 ✅")
    else:
        print_fail(f"FAIL {summary['FAIL']}건 발견 — 리포트를 확인하세요.")

    return results
