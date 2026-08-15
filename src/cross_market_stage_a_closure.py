"""Structural-only helpers for the CM_001 Stage A closure audit.

This module deliberately works with dates, field presence, official classifications,
and provider metadata. It never constructs a research feature, target, or return.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import pandas as pd


RESEARCH_START = date(2010, 1, 1)
RESEARCH_END = date(2018, 12, 31)
REGULAR_TRADING_UNIT = 1_000
OHLC_SOURCE_FIELDS = (
    "Opening Price",
    "Highest Price",
    "Lowest Price",
    "Closing Price",
)


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object with UTF-8 BOM tolerance."""
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def roc_date(value: str) -> date:
    """Convert a TWSE Republic-of-China date to a Gregorian date."""
    parts = value.replace("日", "").replace("月", "-").replace("年", "-").split("-")
    if len(parts) != 3:
        raise ValueError(f"Unexpected ROC date: {value!r}")
    return date(int(parts[0]) + 1911, int(parts[1]), int(parts[2]))


def assert_research_dates(values: Iterable[date], *, label: str) -> None:
    """Reject any date outside the authorized CM_001 Research boundary."""
    dates = list(values)
    if not dates:
        return
    if min(dates) < RESEARCH_START or max(dates) > RESEARCH_END:
        raise ValueError(
            f"{label} crosses Research boundary: min={min(dates)}, max={max(dates)}"
        )


def _int_field(value: Any) -> int:
    return int(str(value).replace(",", "").strip())


def load_twse_stock_day(paths: Iterable[Path], instrument: str) -> pd.DataFrame:
    """Load official STOCK_DAY fields without converting or imputing OHLC."""
    rows: list[dict[str, Any]] = []
    expected = {
        "Date",
        "Trade Volume",
        "Trade Value",
        "Opening Price",
        "Highest Price",
        "Lowest Price",
        "Closing Price",
        "Change",
        "Transaction",
        "Mark",
    }
    for path in sorted(paths):
        payload = load_json(path)
        if payload.get("stat") != "OK":
            continue
        fields = payload.get("fields")
        data = payload.get("data")
        if not isinstance(fields, list) or not expected.issubset(fields):
            raise ValueError(f"{path} missing STOCK_DAY fields")
        if not isinstance(data, list):
            raise ValueError(f"{path} STOCK_DAY data is not a list")
        for values in data:
            if not isinstance(values, list) or len(values) != len(fields):
                raise ValueError(f"{path} contains an invalid STOCK_DAY row")
            record = dict(zip(fields, values))
            record["session_date"] = pd.to_datetime(
                record.pop("Date"), format="%Y/%m/%d"
            ).date()
            record["instrument"] = instrument
            rows.append(record)
    frame = pd.DataFrame(rows)
    frame = frame.loc[
        frame["session_date"].between(RESEARCH_START, RESEARCH_END)
    ].sort_values("session_date").reset_index(drop=True)
    if frame.empty:
        raise ValueError(f"No official STOCK_DAY rows found for {instrument}")
    assert_research_dates(frame["session_date"], label=f"TWSE STOCK_DAY {instrument}")
    if frame["session_date"].duplicated().any():
        raise ValueError(f"Duplicate official STOCK_DAY sessions for {instrument}")
    for field in OHLC_SOURCE_FIELDS:
        frame[f"{field}_available"] = frame[field].ne("--") & frame[field].notna()
    frame["trade_volume_int"] = frame["Trade Volume"].map(_int_field)
    frame["trade_value_int"] = frame["Trade Value"].map(_int_field)
    frame["transactions_int"] = frame["Transaction"].map(_int_field)
    return frame


def load_twse_taiex_presence(paths: Iterable[Path]) -> pd.DataFrame:
    """Load only dates and OHLC-presence flags from official TAIEX responses."""
    rows: list[dict[str, Any]] = []
    expected = [
        "Date",
        "Opening Index",
        "Highest Index",
        "Lowest Index",
        "Closing Index",
    ]
    for path in sorted(paths):
        payload = load_json(path)
        if payload.get("stat") != "OK":
            continue
        if payload.get("fields") != expected:
            raise ValueError(f"{path} has unexpected TAIEX fields")
        for values in payload.get("data", []):
            if not isinstance(values, list) or len(values) != len(expected):
                raise ValueError(f"{path} contains an invalid TAIEX row")
            row = dict(zip(expected, values))
            rows.append(
                {
                    "session_date": pd.to_datetime(
                        row["Date"], format="%Y/%m/%d"
                    ).date(),
                    "open_available": row["Opening Index"] not in (None, "--"),
                    "close_available": row["Closing Index"] not in (None, "--"),
                }
            )
    frame = pd.DataFrame(rows)
    frame = frame.loc[
        frame["session_date"].between(RESEARCH_START, RESEARCH_END)
    ].sort_values("session_date").reset_index(drop=True)
    assert_research_dates(frame["session_date"], label="TWSE TAIEX")
    if frame["session_date"].duplicated().any():
        raise ValueError("Duplicate official TAIEX sessions")
    return frame


def classify_0052_missing(stock_day: pd.DataFrame) -> pd.DataFrame:
    """Classify official all-OHLC sentinels using same-row trading fields only."""
    missing = ~stock_day[[f"{field}_available" for field in OHLC_SOURCE_FIELDS]].any(axis=1)
    work = stock_day.loc[missing].copy()
    classifications: list[str] = []
    reasons: list[str] = []
    for row in work.itertuples(index=False):
        if row.trade_volume_int == row.trade_value_int == row.transactions_int == 0:
            classifications.append("NO_0052_TRADE")
            reasons.append("official volume=value=transactions=0; all official OHLC='--'")
        elif (
            0 < row.trade_volume_int < REGULAR_TRADING_UNIT
            and row.trade_value_int > 0
            and row.transactions_int > 0
        ):
            classifications.append("NO_REGULAR_0052_TRADE_ODD_LOT_ONLY")
            reasons.append(
                "official volume is below the 1,000-unit regular trading unit; "
                "activity exists but official regular OHLC remains '--'"
            )
        else:
            classifications.append("UNRESOLVED")
            reasons.append("official same-row fields do not distinguish the structural cause")
    work["classification"] = classifications
    work["classification_evidence"] = reasons
    output_columns = [
        "session_date",
        "Trade Volume",
        "Trade Value",
        "Transaction",
        "Opening Price",
        "Highest Price",
        "Lowest Price",
        "Closing Price",
        "Change",
        "Mark",
        "classification",
        "classification_evidence",
    ]
    result = work[output_columns].reset_index(drop=True)
    if len(result) != 108:
        raise ValueError(f"Expected 108 official 0052 no-OHLC rows, found {len(result)}")
    return result


def annual_missing_distribution(
    stock_day: pd.DataFrame, missing: pd.DataFrame
) -> pd.DataFrame:
    """Count official sessions and 0052 no-OHLC sessions by year."""
    sessions = stock_day.assign(year=stock_day["session_date"].map(lambda value: value.year))
    missing_years = missing.assign(year=missing["session_date"].map(lambda value: value.year))
    total = sessions.groupby("year").size().rename("official_TW_sessions")
    absent = missing_years.groupby("year").size().rename("0052_no_OHLC_sessions")
    result = pd.concat([total, absent], axis=1).fillna(0).astype(int).reset_index()
    result["fraction_no_OHLC"] = (
        result["0052_no_OHLC_sessions"] / result["official_TW_sessions"]
    )
    return result


def missing_runs(stock_day: pd.DataFrame, missing: pd.DataFrame) -> pd.DataFrame:
    """Identify consecutive no-OHLC runs in the official-session ordering."""
    missing_dates = set(missing["session_date"])
    runs: list[dict[str, Any]] = []
    current: list[date] = []
    for session_date in stock_day["session_date"]:
        if session_date in missing_dates:
            current.append(session_date)
        elif current:
            runs.append(
                {
                    "start_session": current[0],
                    "end_session": current[-1],
                    "official_session_count": len(current),
                }
            )
            current = []
    if current:
        runs.append(
            {
                "start_session": current[0],
                "end_session": current[-1],
                "official_session_count": len(current),
            }
        )
    return pd.DataFrame(runs)


def load_missing_crosscheck(
    closure_root: Path, primary_missing: pd.DataFrame
) -> pd.DataFrame:
    """Compare a pre-specified missing-date sample with official MI_INDEX rows."""
    primary = primary_missing.set_index("session_date")
    rows: list[dict[str, Any]] = []
    for path in sorted(closure_root.glob("twse_mi_index_0052_????????.json")):
        payload = load_json(path)
        session_date = date.fromisoformat(str(payload["requested_date"]))
        assert_research_dates([session_date], label="MI_INDEX cross-check")
        fields = payload["fields"]
        values = payload["data"][0]
        record = dict(zip(fields, values))
        source = primary.loc[session_date]
        agreements = [
            str(record["Trade Volume"]) == str(source["Trade Volume"]),
            str(record["Trade Value"]) == str(source["Trade Value"]),
            str(record["Transaction"]) == str(source["Transaction"]),
            all(str(record[field]) == str(source[field]) for field in OHLC_SOURCE_FIELDS),
        ]
        rows.append(
            {
                "session_date": session_date,
                "primary_classification": source["classification"],
                "second_official_endpoint": "MI_INDEX Daily Quotes (ALL)",
                "crosscheck_status": (
                    "official source agrees" if all(agreements) else "official source disagrees"
                ),
                "trade_volume": record["Trade Volume"],
                "transactions": record["Transaction"],
                "last_best_bid": record.get("Last Best Bid Price", ""),
                "last_best_ask": record.get("Last Best Ask Price", ""),
                "raw_artifact_path": path.as_posix(),
            }
        )
    return pd.DataFrame(rows).sort_values("session_date").reset_index(drop=True)


def load_corporate_action_master(closure_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build and cross-check the official 0052/0050 distribution master."""
    primary_path = closure_root / "twse_ex_right_2010_2018.json"
    primary = load_json(primary_path)
    primary_rows = [dict(zip(primary["fields"], row)) for row in primary["data"]]
    secondary_by_instrument: dict[str, dict[date, Mapping[str, Any]]] = {}
    secondary_paths: dict[str, Path] = {}
    for instrument in ("0052", "0050"):
        path = closure_root / f"twse_etf_div_{instrument}_2010_2018.json"
        payload = load_json(path)
        records = [dict(zip(payload["fields"], row)) for row in payload["data"]]
        secondary_by_instrument[instrument] = {
            roc_date(str(record["除息交易日"])): record for record in records
        }
        secondary_paths[instrument] = path

    master_rows: list[dict[str, Any]] = []
    crosscheck_rows: list[dict[str, Any]] = []
    for record in primary_rows:
        instrument = str(record["股票代號"])
        event_date = roc_date(str(record["資料日期"]))
        assert_research_dates([event_date], label="corporate action master")
        event_marker = str(record["權/息"])
        event_type = {
            "息": "CASH_DISTRIBUTION",
            "權": "EX_RIGHT",
            "權息": "EX_RIGHT_AND_DISTRIBUTION",
        }.get(event_marker, "UNRESOLVED")
        secondary = secondary_by_instrument[instrument].get(event_date)
        primary_amount = str(record["權值+息值"])
        secondary_amount = str(secondary["收益分配金額 (每1受益權益單位)"]) if secondary else ""
        amounts_agree = False
        if secondary:
            amounts_agree = abs(float(primary_amount) - float(secondary_amount)) < 1e-9
        confidence = "CROSS_CHECKED" if secondary and amounts_agree else "CONFIRMED_OFFICIAL"
        master_rows.append(
            {
                "instrument": instrument,
                "event_date": event_date,
                "event_type": event_type,
                "source": "TWSE TWT49U; TWSE ETF/etfDiv",
                "source_authority": "TWSE_OFFICIAL_PRIMARY_AND_SECONDARY",
                "cash_distribution": primary_amount if event_type == "CASH_DISTRIBUTION" else "",
                "split_ratio": "",
                "confidence": confidence,
                "primary_raw_artifact_path": primary_path.as_posix(),
                "secondary_raw_artifact_path": secondary_paths[instrument].as_posix(),
            }
        )
        crosscheck_rows.append(
            {
                "instrument": instrument,
                "event_date": event_date,
                "primary_amount": primary_amount,
                "secondary_amount": secondary_amount,
                "crosscheck_status": (
                    "official source agrees"
                    if secondary and amounts_agree
                    else "official source disagrees"
                    if secondary
                    else "unable to verify"
                ),
            }
        )
    master = pd.DataFrame(master_rows).sort_values(["instrument", "event_date"])
    crosscheck = pd.DataFrame(crosscheck_rows).sort_values(["instrument", "event_date"])
    if len(master.loc[master["instrument"].eq("0052")]) != 6:
        raise ValueError("Expected six official 0052 corporate actions in Research")
    if len(master.loc[master["instrument"].eq("0050")]) != 11:
        raise ValueError("Expected eleven official 0050 corporate actions in Research")
    if not crosscheck["crosscheck_status"].eq("official source agrees").all():
        raise ValueError("Official corporate-action endpoints do not fully agree")
    return master.reset_index(drop=True), crosscheck.reset_index(drop=True)


def build_corporate_action_impacts(
    sessions: pd.Series, master: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Map official 0052 events to price legs without calculating those legs."""
    ordered = list(sessions)
    assert_research_dates(ordered, label="corporate action impact sessions")
    position = {session: index for index, session in enumerate(ordered)}
    events = master.loc[master["instrument"].eq("0052")]
    h1_rows: list[dict[str, Any]] = []
    prev_rows: list[dict[str, Any]] = []
    h2_rows: list[dict[str, Any]] = []
    for event in events.itertuples(index=False):
        event_position = position[event.event_date]
        h1_rows.append(
            {
                "target_session": event.event_date,
                "event_date": event.event_date,
                "event_type": event.event_type,
                "affected_leg": "H1",
            }
        )
        if event_position + 1 >= len(ordered):
            raise ValueError(f"No following session for event {event.event_date}")
        prev_rows.append(
            {
                "target_session": ordered[event_position + 1],
                "event_date": event.event_date,
                "event_type": event.event_type,
                "affected_leg": "PrevTWRel/H3",
            }
        )
        h2_rows.append(
            {
                "target_session": event.event_date,
                "event_date": event.event_date,
                "event_type": event.event_type,
                "affected_leg": "H2 interpretation only",
                "automatic_exclusion": False,
                "reason": "event reference-price reset precedes the regular open; raw same-session Open-Close does not cross the event",
            }
        )
    return pd.DataFrame(h1_rows), pd.DataFrame(prev_rows), pd.DataFrame(h2_rows)


def build_attrition(
    mapping_path: Path,
    follower: pd.DataFrame,
    taiex: pd.DataFrame,
    master: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Determine component presence and mutually exclusive attrition only."""
    mapping = pd.read_csv(mapping_path)
    mapping["session_date"] = pd.to_datetime(mapping["target_session"]).dt.date
    assert_research_dates(mapping["session_date"], label="session mapping")
    follower_presence = follower[
        ["session_date", "Opening Price_available", "Closing Price_available"]
    ].rename(
        columns={
            "Opening Price_available": "open_0052",
            "Closing Price_available": "close_0052",
        }
    )
    frame = (
        mapping[["session_date", "mapping_status", "n_us_sessions"]]
        .merge(follower_presence, on="session_date", how="left", validate="one_to_one")
        .merge(
            taiex.rename(
                columns={"open_available": "open_taiex", "close_available": "close_taiex"}
            ),
            on="session_date",
            how="left",
            validate="one_to_one",
        )
        .sort_values("session_date")
        .reset_index(drop=True)
    )
    if len(frame) != 2_223 or frame.isna().any().any():
        raise ValueError("Attrition ledger does not contain 2,223 complete presence rows")
    frame["first_session_boundary"] = frame.index == 0
    frame["eligible_us"] = frame["mapping_status"].eq("VALID")
    frame["empty_us_window"] = frame["mapping_status"].eq("EMPTY_US_WINDOW")
    frame["broad_tech_available"] = frame["eligible_us"]
    frame["previous_close_0052"] = frame["close_0052"].shift(1, fill_value=False)
    frame["previous2_close_0052"] = frame["close_0052"].shift(2, fill_value=False)
    frame["previous_close_taiex"] = frame["close_taiex"].shift(1, fill_value=False)
    frame["previous2_close_taiex"] = frame["close_taiex"].shift(2, fill_value=False)

    event_dates = set(
        master.loc[master["instrument"].eq("0052"), "event_date"].tolist()
    )
    frame["h1_corporate_action_candidate"] = frame["session_date"].isin(event_dates)
    frame["h3_corporate_action_candidate"] = frame["session_date"].shift(1).isin(event_dates)

    frame["h1_input_available"] = (
        frame["eligible_us"]
        & frame["open_0052"]
        & frame["previous_close_0052"]
        & frame["open_taiex"]
        & frame["previous_close_taiex"]
        & ~frame["first_session_boundary"]
    )
    frame["h2_input_available"] = (
        frame["eligible_us"]
        & frame["open_0052"]
        & frame["close_0052"]
        & frame["open_taiex"]
        & frame["close_taiex"]
    )
    frame["prevtwrel_input_available"] = (
        frame["previous_close_0052"]
        & frame["previous2_close_0052"]
        & frame["previous_close_taiex"]
        & frame["previous2_close_taiex"]
    )
    frame["h3_input_available"] = (
        frame["h2_input_available"]
        & frame["broad_tech_available"]
        & frame["prevtwrel_input_available"]
    )
    frame["h1_usable_under_candidate_policy"] = (
        frame["h1_input_available"] & ~frame["h1_corporate_action_candidate"]
    )
    frame["h2_usable_under_candidate_policy"] = frame["h2_input_available"]
    frame["h3_usable_under_candidate_policy"] = (
        frame["h3_input_available"] & ~frame["h3_corporate_action_candidate"]
    )

    waterfall_rows = [
        {"Stage": "session ledger", "count": len(frame), "excluded": 0, "reason": "none"},
        {
            "Stage": "after empty-US-window rule",
            "count": int((~frame["empty_us_window"]).sum()),
            "excluded": int(frame["empty_us_window"].sum()),
            "reason": "no eligible US session",
        },
        {
            "Stage": "eligible US window",
            "count": int(frame["eligible_us"].sum()),
            "excluded": int(frame["first_session_boundary"].sum()),
            "reason": "first-session boundary has no previous Taiwan close",
        },
        {
            "Stage": "H1 raw-input availability",
            "count": int(frame["h1_input_available"].sum()),
            "excluded": int(frame["eligible_us"].sum() - frame["h1_input_available"].sum()),
            "reason": "required Open/previous Close presence only",
        },
        {
            "Stage": "H1 under candidate action policy",
            "count": int(frame["h1_usable_under_candidate_policy"].sum()),
            "excluded": int(
                (frame["h1_input_available"] & frame["h1_corporate_action_candidate"]).sum()
            ),
            "reason": "confirmed corporate-action crossing; policy not approved",
        },
        {
            "Stage": "H2 raw-input availability",
            "count": int(frame["h2_input_available"].sum()),
            "excluded": int(frame["eligible_us"].sum() - frame["h2_input_available"].sum()),
            "reason": "required same-session Open/Close presence only",
        },
        {
            "Stage": "H3 raw-input availability",
            "count": int(frame["h3_input_available"].sum()),
            "excluded": int(frame["h2_input_available"].sum() - frame["h3_input_available"].sum()),
            "reason": "BroadTech and PrevTWRel input presence only",
        },
        {
            "Stage": "H3 under candidate action policy",
            "count": int(frame["h3_usable_under_candidate_policy"].sum()),
            "excluded": int(
                (frame["h3_input_available"] & frame["h3_corporate_action_candidate"]).sum()
            ),
            "reason": "confirmed corporate-action crossing; policy not approved",
        },
    ]

    reason_rows = [
        {"hypothesis": "H1", "reason": "first-session boundary", "excluded": 1},
        {"hypothesis": "H1", "reason": "no eligible US session", "excluded": 85},
        {
            "hypothesis": "H1",
            "reason": "missing 0052 Open after prior gates",
            "excluded": 103,
        },
        {
            "hypothesis": "H1",
            "reason": "missing 0052 previous Close after prior gates",
            "excluded": 90,
        },
        {"hypothesis": "H1", "reason": "missing TAIEX leg", "excluded": 0},
        {
            "hypothesis": "H1",
            "reason": "corporate-action exclusion candidate",
            "excluded": 6,
        },
        {"hypothesis": "H1", "reason": "other mechanical reason", "excluded": 0},
        {"hypothesis": "H2", "reason": "other: first-session boundary", "excluded": 1},
        {"hypothesis": "H2", "reason": "no eligible US session", "excluded": 85},
        {
            "hypothesis": "H2",
            "reason": "missing 0052 Open (and Close) after prior gates",
            "excluded": 103,
        },
        {
            "hypothesis": "H2",
            "reason": "missing 0052 Close only after prior gates",
            "excluded": 0,
        },
        {"hypothesis": "H2", "reason": "missing TAIEX Open/Close", "excluded": 0},
        {"hypothesis": "H2", "reason": "other mechanical reason", "excluded": 0},
        {"hypothesis": "H3", "reason": "all H2 requirements", "excluded": 189},
        {"hypothesis": "H3", "reason": "missing BroadTech", "excluded": 0},
        {
            "hypothesis": "H3",
            "reason": "missing PrevTWRel leg after H2 gates",
            "excluded": 178,
        },
        {
            "hypothesis": "H3",
            "reason": "corporate-action exclusion candidate",
            "excluded": 6,
        },
        {"hypothesis": "H3", "reason": "other mechanical reason", "excluded": 0},
    ]

    expected = {
        "eligible": 2_137,
        "h1_inputs": 1_944,
        "h1_candidate": 1_938,
        "h2_inputs": 2_034,
        "h3_inputs": 1_856,
        "h3_candidate": 1_850,
    }
    observed = {
        "eligible": int(frame["eligible_us"].sum()),
        "h1_inputs": int(frame["h1_input_available"].sum()),
        "h1_candidate": int(frame["h1_usable_under_candidate_policy"].sum()),
        "h2_inputs": int(frame["h2_input_available"].sum()),
        "h3_inputs": int(frame["h3_input_available"].sum()),
        "h3_candidate": int(frame["h3_usable_under_candidate_policy"].sum()),
    }
    if observed != expected:
        raise ValueError(f"Unexpected mechanical attrition: {observed}")
    return frame, pd.DataFrame(waterfall_rows), pd.DataFrame(reason_rows)


def yahoo_presence(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load Yahoo session dates and field presence without price transformations."""
    payload = load_json(path)
    result = payload["chart"]["result"][0]
    meta = result["meta"]
    quote = result["indicators"]["quote"][0]
    timestamps = pd.to_datetime(result["timestamp"], unit="s", utc=True)
    local_dates = timestamps.tz_convert(ZoneInfo(meta["exchangeTimezoneName"])).date
    frame = pd.DataFrame(
        {
            "session_date": local_dates,
            "open_available": [value is not None and value > 0 for value in quote["open"]],
            "close_available": [value is not None and value > 0 for value in quote["close"]],
        }
    )
    frame = frame.loc[
        frame["session_date"].between(RESEARCH_START, RESEARCH_END)
    ].reset_index(drop=True)
    assert_research_dates(frame["session_date"], label=f"Yahoo {meta.get('symbol')}")
    return frame, meta


def calendar_audit(
    official_sessions: pd.Series, yahoo_root: Path, mapping_path: Path
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Audit US venue compatibility and official-TWSE versus XTAI dates."""
    official = set(official_sessions)
    calendars: dict[str, pd.DataFrame] = {}
    for name in ("XNYS", "XNAS", "ARCX", "XTAI"):
        calendars[name] = xcals.get_calendar(name).schedule.loc[
            str(RESEARCH_START) : str(RESEARCH_END)
        ].copy()
    base = calendars["XNYS"]
    venue_rows: list[dict[str, Any]] = []
    for name in ("XNYS", "XNAS", "ARCX"):
        schedule = calendars[name]
        venue_rows.append(
            {
                "calendar": name,
                "sessions": len(schedule),
                "same_dates_as_XNYS": schedule.index.equals(base.index),
                "different_opens_vs_XNYS": int((schedule["open"] != base["open"]).sum()),
                "different_closes_vs_XNYS": int((schedule["close"] != base["close"]).sum()),
            }
        )

    raw_rows: list[dict[str, Any]] = []
    for instrument in ("XSD", "QQQ", "SPY"):
        frame, meta = yahoo_presence(yahoo_root / f"{instrument}_response.json")
        raw_dates = set(frame.loc[frame[["open_available", "close_available"]].all(axis=1), "session_date"])
        xnys_dates = set(base.index.date)
        raw_rows.append(
            {
                "instrument": instrument,
                "provider_exchange": meta.get("fullExchangeName"),
                "provider_timezone": meta.get("exchangeTimezoneName"),
                "valid_raw_sessions": len(raw_dates),
                "raw_not_in_XNYS": len(raw_dates - xnys_dates),
                "XNYS_not_in_raw": len(xnys_dates - raw_dates),
            }
        )

    xtai_dates = set(calendars["XTAI"].index.date)
    official_not_xtai = sorted(official - xtai_dates)
    xtai_not_official = sorted(xtai_dates - official)
    mapping = pd.read_csv(mapping_path)
    mapping_dates = set(pd.to_datetime(mapping["target_session"]).dt.date)
    detail = {
        "exchange_calendars_version": xcals.__version__,
        "official_twse_sessions": len(official),
        "xnys_sessions": len(base),
        "xnys_early_closes": int(
            ((base["close"] - base["open"]) < (base["close"] - base["open"]).mode().iloc[0]).sum()
        ),
        "official_not_xtai": [value.isoformat() for value in official_not_xtai],
        "xtai_not_official": [value.isoformat() for value in xtai_not_official],
        "official_not_xtai_all_retained_by_mapper": set(official_not_xtai).issubset(mapping_dates),
        "xtai_extra_excluded_from_mapper": set(xtai_not_official).isdisjoint(mapping_dates),
        "taiwan_regular_open": "09:00 Asia/Taipei",
        "taiwan_regular_close": "13:30 Asia/Taipei",
        "taiwan_early_close_found": False,
        "taiwan_extraordinary_session_hours_found": False,
        "calendar_policy_exception_required": False,
        "security_level_close_auction_note": (
            "TWSE documents a possible security-level closing-auction postponement to 13:33 "
            "from 2012-02-20; it is not a session-calendar early close and cannot alter the "
            "eligible US-session set because the next US open is hours later."
        ),
    }
    return pd.DataFrame(venue_rows), pd.DataFrame(raw_rows), detail


def raw_adjusted_evidence(yahoo_root: Path) -> pd.DataFrame:
    """Document raw/adjusted field availability and provider semantics."""
    rows: list[dict[str, Any]] = []
    for instrument in ("XSD", "QQQ", "SPY", "0052", "TAIEX", "0050"):
        payload = load_json(yahoo_root / f"{instrument}_response.json")
        result = payload["chart"]["result"][0]
        quote = result["indicators"]["quote"][0]
        adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose", [])
        rows.append(
            {
                "source": "Yahoo Chart API",
                "instrument": instrument,
                "raw_Open_available": any(value is not None for value in quote["open"]),
                "raw_Close_available": any(value is not None for value in quote["close"]),
                "Adj_Close_available": any(value is not None for value in adj),
                "historical_adjustment_mechanism_known": True,
                "dividends_included_in_Adj_Close": True,
                "splits_included": True,
                "Open_adjusted_consistently": False,
                "provider_documentation_found": True,
                "scale_discontinuities": (
                    "2014-01-02 boundary in Yahoo 0050 raw history vs official TWSE (4x scale)"
                    if instrument == "0050"
                    else "0052 raw Open has nonpositive/missing records"
                    if instrument == "0052"
                    else "none identified in structural session audit"
                ),
                "policy_note": "Adj Close is separate; never pair it with raw Open",
            }
        )
    for instrument in ("0052", "0050", "TAIEX"):
        raw_availability = (
            "PARTIAL (2115/2223; 108 official no-regular-OHLC rows)"
            if instrument == "0052"
            else "YES (2223/2223)"
        )
        rows.append(
            {
                "source": "TWSE official",
                "instrument": instrument,
                "raw_Open_available": raw_availability,
                "raw_Close_available": raw_availability,
                "Adj_Close_available": False,
                "historical_adjustment_mechanism_known": False,
                "dividends_included_in_Adj_Close": False,
                "splits_included": False,
                "Open_adjusted_consistently": True,
                "provider_documentation_found": True,
                "scale_discontinuities": (
                    "108 official no-regular-OHLC rows, explicitly classified"
                    if instrument == "0052"
                    else "none in official Research raw scale"
                ),
                "policy_note": "official raw OHLC; actions maintained separately",
            }
        )
    return pd.DataFrame(rows)


def audit_0050_provider_scale(
    official_stock_day: pd.DataFrame, yahoo_response_path: Path
) -> dict[str, Any]:
    """Locate cross-provider price-scale regimes without calculating returns."""
    payload = load_json(yahoo_response_path)
    result = payload["chart"]["result"][0]
    timezone = ZoneInfo(result["meta"]["exchangeTimezoneName"])
    yahoo = pd.DataFrame(
        {
            "session_date": pd.to_datetime(result["timestamp"], unit="s", utc=True)
            .tz_convert(timezone)
            .date,
            "yahoo_close": result["indicators"]["quote"][0]["close"],
        }
    )
    yahoo = yahoo.loc[yahoo["session_date"].between(RESEARCH_START, RESEARCH_END)]
    official = official_stock_day[["session_date", "Closing Price"]].copy()
    official["official_close"] = pd.to_numeric(
        official["Closing Price"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    joined = official[["session_date", "official_close"]].merge(
        yahoo, on="session_date", how="inner", validate="one_to_one"
    ).dropna()
    joined["scale_ratio"] = joined["official_close"] / joined["yahoo_close"]
    unit = joined["scale_ratio"].sub(1.0).abs().le(0.005)
    four = joined["scale_ratio"].sub(4.0).abs().le(0.005)
    other = ~(unit | four)
    return {
        "comparable_sessions": int(len(joined)),
        "approximately_1x_sessions": int(unit.sum()),
        "approximately_4x_sessions": int(four.sum()),
        "other_scale_sessions": int(other.sum()),
        "last_1x_session": joined.loc[unit, "session_date"].max().isoformat(),
        "first_4x_session": joined.loc[four, "session_date"].min().isoformat(),
    }
