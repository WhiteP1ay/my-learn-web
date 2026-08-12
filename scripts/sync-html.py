#!/usr/bin/env python3
"""Sync data/*.json → docs/index.html inline DATA object.

Run after updating curriculum.json or learning-state.json to keep the
GitHub Pages rendering in sync with the data layer.
"""

import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(name):
    with open(ROOT / 'data' / name) as f:
        return json.load(f)


def extract_plans(html):
    """Extract existing plans from HTML DATA to preserve across syncs."""
    m = re.search(r'"plans":\s*\{', html)
    if not m:
        return {}
    start = m.start()
    depth = 0
    for i in range(start, len(html)):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                json_str = '{' + html[start: i+1].split('{', 1)[1]
                return json.loads(json_str)
    return {}


def main():
    curriculum = load_json('curriculum.json')
    state = load_json('learning-state.json')

    # Read current HTML
    html_path = ROOT / 'docs' / 'index.html'
    with open(html_path) as f:
        html = f.read()

    old_plans = extract_plans(html)

    # Build new chapter name set
    new_names = set()
    for phase in curriculum['phases']:
        for group in phase['groups']:
            for ch in group['chapters']:
                new_names.add(ch['name'])

    # Keep plans matching new chapter names
    kept_plans = {}
    for name, plan in old_plans.items():
        if name in new_names:
            kept_plans[name] = plan

    # Build phases
    PHASE_IDS = {'phase1': 'p1', 'phase2': 'p2', 'phase3': 'p3', 'phase4': 'p4'}
    phases = []
    for phase in curriculum['phases']:
        pid = PHASE_IDS.get(phase['id'], phase['id'])
        name = phase['name']
        for prefix in ['Phase 1: ', 'Phase 2: ', 'Phase 3: ', 'Phase 4: ']:
            name = name.replace(prefix, '')
        pd = {'id': pid, 'name': name, 'groups': []}
        for group in phase['groups']:
            gd = {'name': group['name'], 'chapters': []}
            for ch in group['chapters']:
                gd['chapters'].append({
                    'id': ch['id'],
                    'name': ch['name'],
                    'done': ch.get('mastery', 0) >= 3
                })
            pd['groups'].append(gd)
        phases.append(pd)

    # Review pool
    review_pool = []
    for item in state.get('review_pool', []):
        review_pool.append({
            'id': item['chapter_id'],
            'name': item.get('chapter_name', ''),
            'last': item.get('last_review', ''),
            'gap': item.get('gap', '')
        })

    # Meta
    upcoming = state.get('upcoming_plan', [''])
    meta = {
        'position': upcoming[0] if upcoming else '',
        'project': curriculum['meta'].get('project_spine', '')
    }

    new_data = {
        'phases': phases,
        'review_pool': review_pool,
        'meta': meta,
        'memory': [],
        'plans': kept_plans
    }

    new_data_json = json.dumps(new_data, ensure_ascii=False, indent=2)
    new_html = re.sub(
        r'const DATA = \{[\s\S]*?\n\};',
        'const DATA = ' + new_data_json + ';',
        html, count=1
    )

    with open(html_path, 'w') as f:
        f.write(new_html)

    total = sum(len(g['chapters']) for p in phases for g in p['groups'])
    print(f"Synced: {total} chapters, {len(review_pool)} reviews, {len(kept_plans)} plans")


if __name__ == '__main__':
    main()
