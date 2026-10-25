#!/usr/bin/env python3
"""Flag any number in a tailored resume (or interview guide) that is not in the master resume.

Usage:
  python3 number_check.py profile.json FILE.pdf [FILE.pdf ...]
  python3 number_check.py profile.json --guide guide.json Interview_Guide_X.pdf

profile.json is the `meta/profile` document saved from the tracker (it holds `master`, `name`, `phone`).
Every number in the output must appear somewhere in the master resume or the contact line. For a guide,
numbers from its own snapshot, date, stage, logistics and questions are allowed too. Anything printed as
NOT IN MASTER is a bug: fix the JSON and re-render.
"""
import json, re, subprocess, sys

NUM = r"\d+(?:\.\d+)?"


def nums(text):
    return set(re.findall(NUM, str(text).replace(",", "")))


def main():
    a = sys.argv[1:]
    prof = json.load(open(a.pop(0)))
    prof = prof.get("data", prof)
    ok = nums(json.dumps(prof.get("master", {}))) | nums(prof.get("phone", "")) | nums(json.dumps(prof.get("contact", [])))
    ok |= {"1", "2"}  # page numbers, "2 pages"
    if a and a[0] == "--guide":
        a.pop(0)
        g = json.load(open(a.pop(0)))
        extra = " ".join(g.get("snapshot", []) + g.get("logistics", []) + g.get("ask_them", []) + [g.get("date", ""), g.get("stage", "")])
        ok |= nums(extra) | {"30", "31", "60", "61", "90"}
    bad_any = False
    for f in a:
        t = subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout
        bad = sorted(nums(t) - ok, key=lambda x: float(x))
        print(f, "OK" if not bad else f"NOT IN MASTER: {bad}")
        bad_any |= bool(bad)
    sys.exit(1 if bad_any else 0)


if __name__ == "__main__":
    main()
