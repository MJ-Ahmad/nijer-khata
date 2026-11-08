#!/usr/bin/env python3
"""Self / Life Tracker — command line and storage library (owner: mj-ahmad).

  python3 life.py log "one line of progress or a thought" [--category C] [--mood 1-5]
  python3 life.py add "Heading" "Description" [--body-file notes.md] [--category C]
                      [--mood 1-5] [--tag a,b] [--link TASK-000001] [--add-file PATH]
  python3 life.py list [--limit N]
  python3 life.py validate
"""

import os
import re
import sys
import json
import shutil
import hashlib
import mimetypes
import tempfile
import argparse
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data.json")
REGISTRY_FILE = os.path.join(BASE, "registry.json")
ATTACH_DIR = os.path.join(BASE, "attachments")

DHAKA = timezone(timedelta(hours=6))  # Asia/Dhaka, UTC+06:00, no DST
TS_FMT = "%Y-%m-%d %H:%M:%S.%f"
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$")
TRACK_RE = re.compile(r"^LIFE-\d{6}$")
REG_RE = re.compile(r"^REG-\d{6}$")
LINK_RE = re.compile(r"^[A-Z]+-\d{6}$")
CATEGORIES = ["health", "learning", "work", "habits", "relationships",
              "faith", "finance", "reflection", "other"]
HEADING_MAX = 80


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def now_stamps():
    utc = datetime.now(timezone.utc)
    return utc.astimezone(DHAKA).strftime(TS_FMT)[:-3], utc.strftime(TS_FMT)[:-3]


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_atomic(path, data):
    """Write to a temp file, then replace: a crash never leaves a broken JSON."""
    fd, tmp = tempfile.mkstemp(dir=BASE, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def allocate_ids():
    """Advance both counters together; returns (LIFE-id, REG-id)."""
    reg = load(REGISTRY_FILE, {"last_registry": 0, "last_tracking": 0})
    reg["last_registry"] = reg.get("last_registry", 0) + 1
    reg["last_tracking"] = reg.get("last_tracking", 0) + 1
    save_atomic(REGISTRY_FILE, reg)
    return f"LIFE-{reg['last_tracking']:06}", f"REG-{reg['last_registry']:06}"


def store_attachment(reg_id, src):
    os.makedirs(ATTACH_DIR, exist_ok=True)
    original = os.path.basename(src)
    name = f"{reg_id}{os.path.splitext(original)[1].lower()}"
    dest = os.path.join(ATTACH_DIR, name)
    shutil.copy2(src, dest)
    return {
        "file": f"attachments/{name}",
        "original": original,
        "size": os.path.getsize(dest),
        "type": mimetypes.guess_type(dest)[0] or "application/octet-stream",
        "sha256": sha256(dest),
    }


def split_list(text):
    """'a, b,  a' -> ['a', 'b'] (lowercased, de-duplicated)."""
    out = []
    for item in (text or "").split(","):
        item = item.strip().lower()
        if item and item not in out:
            out.append(item)
    return out


def derive_heading(text):
    heading = " ".join(text.split()[:8])
    if len(heading) > HEADING_MAX:
        heading = heading[:HEADING_MAX].rsplit(" ", 1)[0] + "…"
    return heading


def create_entry(heading, description, args):
    heading = " ".join(heading.split())
    description = description.strip()
    if not heading:
        fail("heading must not be empty")
    if len(heading) > HEADING_MAX:
        fail(f"heading must be {HEADING_MAX} characters or fewer")
    if not description:
        fail("description must not be empty (or use --body-file)")
    if args.category not in CATEGORIES:
        fail(f"unknown category '{args.category}'")
    if args.mood is not None and not 1 <= args.mood <= 5:
        fail("mood must be between 1 and 5")
    links = [x.upper() for x in split_list(args.link)]
    for link in links:
        if not LINK_RE.match(link):
            fail(f"bad link reference '{link}' (expected e.g. TASK-000001)")
    if args.add_file and not os.path.isfile(args.add_file):
        fail(f"file not found: {args.add_file}")

    tracking_id, reg_id = allocate_ids()
    dhaka, utc = now_stamps()
    entry = {
        "tracking_id": tracking_id,
        "registry": reg_id,
        "dhaka_time": dhaka,
        "utc_time": utc,
        "category": args.category,
        "mood": args.mood,
        "heading": heading,
        "description": description,
        "tags": split_list(args.tag),
        "links": links,
    }
    if args.add_file:
        entry["attachment"] = store_attachment(reg_id, args.add_file)

    data = load(DATA_FILE, {"entries": []})
    data["entries"].insert(0, entry)
    save_atomic(DATA_FILE, data)
    return entry


def cmd_log(args):
    entry = create_entry(derive_heading(args.text), args.text, args)
    report(entry)


def cmd_add(args):
    description = args.description
    if args.body_file:
        if not os.path.isfile(args.body_file):
            fail(f"body file not found: {args.body_file}")
        with open(args.body_file, encoding="utf-8") as f:
            description = f.read()
    report(create_entry(args.heading, description or "", args))


def cmd_list(args):
    entries = load(DATA_FILE, {"entries": []})["entries"][: args.limit]
    for e in entries:
        print(f"{e['tracking_id']}  {e['registry']}  {e['dhaka_time']}  {e['heading']}")


def report(entry):
    print("\nEntry added")
    print(f"  Tracking : {entry['tracking_id']}")
    print(f"  Registry : {entry['registry']}")
    print(f"  Dhaka    : {entry['dhaka_time']}")
    print(f"  UTC      : {entry['utc_time']}")
    if "attachment" in entry:
        print(f"  File     : {entry['attachment']['original']}")
    print()


def validate():
    """Return (errors, warnings). No errors means the database is sound."""
    errors, warnings = [], []
    data = load(DATA_FILE, None)
    registry = load(REGISTRY_FILE, None)
    if data is None or registry is None:
        return ["data.json or registry.json is missing"], warnings
    entries = data.get("entries")
    if not isinstance(entries, list):
        return ["'entries' must be a list"], warnings

    seen_t, seen_r = set(), set()
    max_t = max_r = 0
    for e in entries:
        tid = str(e.get("tracking_id", "<missing>"))
        rid = str(e.get("registry", "<missing>"))
        if not TRACK_RE.match(tid):
            errors.append(f"{tid}: bad tracking_id")
        elif tid in seen_t:
            errors.append(f"{tid}: duplicate tracking_id")
        else:
            seen_t.add(tid)
            max_t = max(max_t, int(tid[5:]))
        if not REG_RE.match(rid):
            errors.append(f"{tid}: bad registry id ({rid})")
        elif rid in seen_r:
            errors.append(f"{tid}: duplicate registry id ({rid})")
        else:
            seen_r.add(rid)
            max_r = max(max_r, int(rid[4:]))
        for key in ("dhaka_time", "utc_time"):
            if not TS_RE.match(str(e.get(key, ""))):
                errors.append(f"{tid}: invalid {key}")
        if not str(e.get("heading", "")).strip():
            errors.append(f"{tid}: empty heading")
        if not str(e.get("description", "")).strip():
            errors.append(f"{tid}: empty description")
        if e.get("category", "other") not in CATEGORIES:
            errors.append(f"{tid}: unknown category")
        mood = e.get("mood")
        if mood is not None and (not isinstance(mood, int) or not 1 <= mood <= 5):
            errors.append(f"{tid}: mood must be 1-5")
        for link in e.get("links", []):
            if not LINK_RE.match(str(link)):
                errors.append(f"{tid}: bad link '{link}'")
        att = e.get("attachment")
        if att:
            path = os.path.join(BASE, att.get("file", ""))
            if att.get("missing"):
                warnings.append(f"{tid}: file not in this copy ({att.get('original')})")
            elif not os.path.isfile(path):
                errors.append(f"{tid}: attachment missing ({att.get('file')})")
            elif sha256(path) != att.get("sha256"):
                errors.append(f"{tid}: checksum mismatch ({att.get('file')})")

    if registry.get("last_tracking", 0) < max_t:
        errors.append("registry.last_tracking is behind the highest LIFE id")
    if registry.get("last_registry", 0) < max_r:
        errors.append("registry.last_registry is behind the highest REG id")
    return errors, warnings


def cmd_validate(_args):
    errors, warnings = validate()
    for w in warnings:
        print(f"  warning: {w}")
    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        print(f"\nValidation failed with {len(errors)} error(s).")
        sys.exit(1)
    data = load(DATA_FILE, {"entries": []})
    print(f"Database valid · entries: {len(data['entries'])}")


def main():
    parser = argparse.ArgumentParser(prog="life.py", description="Self / Life Tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def shared(sp):
        sp.add_argument("--category", default="other", choices=CATEGORIES)
        sp.add_argument("--mood", type=int)
        sp.add_argument("--tag", default="", help="comma separated tags")
        sp.add_argument("--link", default="", help="comma separated IDs, e.g. TASK-000001")
        sp.add_argument("--add-file", metavar="PATH", help="attach a file (copied, checksummed)")

    lg = sub.add_parser("log", help="quick one-line entry")
    lg.add_argument("text")
    shared(lg)
    lg.set_defaults(func=cmd_log)

    ad = sub.add_parser("add", help="full entry with heading and description")
    ad.add_argument("heading")
    ad.add_argument("description", nargs="?", default="")
    ad.add_argument("--body-file", help="read the description from a file")
    shared(ad)
    ad.set_defaults(func=cmd_add)

    ls = sub.add_parser("list", help="show latest entries")
    ls.add_argument("--limit", type=int, default=10)
    ls.set_defaults(func=cmd_list)

    vd = sub.add_parser("validate", help="check data integrity")
    vd.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
