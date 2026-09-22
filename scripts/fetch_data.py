"""
fetch_data.py — daily Google Sheets → JSON snapshot
Runs in GitHub Actions; output goes to data/*.json
No API key required (uses public gviz/tq endpoint).
Sheets must be shared as "Anyone with the link can view".
"""

import csv
import io
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ── Sheet IDs (matches CONFIG in index.html) ──
OUTREACH_SHEET_ID  = '10NOima0tcnyRwl4iusBacNomQzmmVvimjyjBiUWykGg'
ONBOARDING_SHEET_ID = '1IYLwgQnj722wSv37KbXzyes9VRaNZ1YYEmnjTtZnd-E'

TABS = [
    ('shivansh',   OUTREACH_SHEET_ID,  'shivansh'),
    ('priya',      OUTREACH_SHEET_ID,  'priya'),
    ('direct',     OUTREACH_SHEET_ID,  'Seller Pro Direct Leads'),
    ('onboarding', ONBOARDING_SHEET_ID, ''),
]


def fetch_sheet_csv(sheet_id: str, tab_name: str = '') -> list[dict]:
    """Fetch a Google Sheet tab as a list of row-dicts."""
    # tq=select * ensures all rows are returned even if a filter is applied on the sheet
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&tq=select%20*'
    if tab_name:
        url += '&sheet=' + urllib.parse.quote(tab_name)

    req = urllib.request.Request(url, headers={'User-Agent': 'celebro-data-sync/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8')

    if raw.startswith('<!'):
        raise ValueError(f'Sheet "{tab_name}" is not public or does not exist')

    reader = csv.DictReader(io.StringIO(raw))
    return [dict(row) for row in reader]


def main():
    os.makedirs('data', exist_ok=True)

    results = {}
    for name, sid, tab in TABS:
        print(f'Fetching {name} (tab="{tab}" from sheet {sid[:8]}…)…', end=' ', flush=True)
        try:
            rows = fetch_sheet_csv(sid, tab)
            out_path = f'data/{name}.json'
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
            results[name] = {'rows': len(rows), 'status': 'ok'}
            print(f'{len(rows)} rows ✓')
        except Exception as e:
            results[name] = {'status': 'error', 'error': str(e)}
            print(f'FAILED — {e}')

    # Write meta.json — dashboard shows this as last-sync time
    now_utc = datetime.now(timezone.utc)
    # Convert to IST for display
    from datetime import timedelta
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset
    meta = {
        'fetched_at': now_ist.strftime('%-d %b %Y, %-I:%M %p IST'),
        'fetched_utc': now_utc.isoformat(),
        'tabs': results,
    }
    with open('data/meta.json', 'w') as f:
        json.dump(meta, f, indent=2)
    print(f'\nMeta written → fetched_at: {meta["fetched_at"]}')

    errors = [k for k, v in results.items() if v['status'] == 'error']
    if errors:
        print(f'\n⚠️  {len(errors)} tab(s) failed: {errors}')
        raise SystemExit(1)

    print('\nAll done.')


if __name__ == '__main__':
    main()
