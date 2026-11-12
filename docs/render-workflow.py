#!/usr/bin/env python3
"""Render this repository's simple Excalidraw scene without external packages.

Run from the repository root: python3 docs/render-workflow.py
This is a bounded preview renderer, not a general Excalidraw implementation.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
scene = json.loads((ROOT / 'provenance-workflow.excalidraw').read_text())
assert scene['type'] == 'excalidraw' and scene['version'] == 2
assert not scene.get('files'), 'No embedded third-party assets expected'
elements = scene['elements']
ids = {e['id'] for e in elements}
assert len(ids) == len(elements), 'Duplicate element IDs'
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 850" role="img" aria-labelledby="title desc">',
       '<title id="title">Humanizer provenance and human review boundary</title>',
       '<desc id="desc">Wikipedia-derived material flows through upstream and the pinned fork to a host editor. Human factual and rights review is required before accepting or publishing a rewrite.</desc>',
       '<rect width="960" height="850" fill="white"/>']
for e in elements:
    assert not e.get('isDeleted')
    x, y, w, h = (e[k] for k in ('x', 'y', 'width', 'height'))
    assert x >= 0 and y >= 0 and x + w <= 960 and y + h <= 850
    if e['type'] == 'rectangle':
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{e["backgroundColor"]}" stroke="{e["strokeColor"]}" stroke-width="2"/>')
    elif e['type'] == 'text':
        for i, line in enumerate(e['text'].splitlines()):
            svg.append(f'<text x="{x}" y="{y + e["fontSize"] + i * e["fontSize"] * e["lineHeight"]}" font-family="Arial, sans-serif" font-size="{e["fontSize"]}" fill="{e["strokeColor"]}">{html.escape(line)}</text>')
    elif e['type'] == 'arrow':
        assert len(e['points']) == 2
        for binding in ('startBinding', 'endBinding'):
            assert e[binding]['elementId'] in ids
        dx, dy = e['points'][1]
        assert dx == 0 and dy > 0
        svg.append(f'<path d="M{x} {y} v{dy} m-6 -8 l6 8 l6 -8" fill="none" stroke="{e["strokeColor"]}" stroke-width="2"/>')
    else:
        raise ValueError(f'Unsupported preview element: {e["type"]}')
svg.append('</svg>')
(ROOT / 'provenance-workflow.svg').write_text('\n'.join(svg) + '\n')
print(f'PASS: {len(elements)} unique, bounded scene elements rendered to SVG')
