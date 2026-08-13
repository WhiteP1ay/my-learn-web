#!/usr/bin/env python3
"""Sync data/*.json → docs/index.html inline DATA object.

Run after updating curriculum.json, learning-state.json, or plans.json
to keep the GitHub Pages rendering in sync with the data layer.
"""

import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(name):
    with open(ROOT / 'data' / name) as f:
        return json.load(f)


def load_plans():
    """Load teaching plans from data/plans.json."""
    p = ROOT / 'data' / 'plans.json'
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def main():
    curriculum = load_json('curriculum.json')
    state = load_json('learning-state.json')
    plans = load_plans()

    # Build new chapter name set (to filter plans)
    new_names = set()
    for phase in curriculum['phases']:
        for group in phase['groups']:
            for ch in group['chapters']:
                new_names.add(ch['name'])

    # Keep plans matching current chapter names
    kept_plans = {k: v for k, v in plans.items() if k in new_names}

    # Build phases
    PHASE_IDS = {'phase1': 'p1', 'phase2': 'p2', 'phase3': 'p3', 'phase4': 'p4'}
    PHASE_SHORT_NAMES = {'phase1': 'Python 后端', 'phase2': 'AI 工程', 'phase3': 'Java 企业', 'phase4': '运维'}
    phases = []
    for phase in curriculum['phases']:
        pid = PHASE_IDS.get(phase['id'], phase['id'])
        name = PHASE_SHORT_NAMES.get(phase['id'], phase['name'])
        pd = {'id': pid, 'name': name, 'groups': []}
        for group in phase['groups']:
            gd = {'name': group['name'], 'chapters': []}
            for ch in group['chapters']:
                gd['chapters'].append({
                    'id': ch['id'],
                    'name': ch['name'],
                    'mastery': ch.get('mastery', 0),
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
    html_path = ROOT / 'docs' / 'index.html'
    with open(html_path) as f:
        html = f.read()

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
