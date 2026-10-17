#!/usr/bin/env python3
"""Export an existing RetroReview SQLite database to a browser-importable JSON backup.

Run this from the original RetroReview project folder, or pass --db explicitly.
Only the selected user's reviews are exported; password hashes and sessions are never exported.
"""
import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def json_value(value, fallback):
    try:
        return json.loads(value) if value else fallback
    except (TypeError, json.JSONDecodeError):
        return fallback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='data/retroreview.sqlite3', help='SQLite database path (default: data/retroreview.sqlite3)')
    parser.add_argument('--email', help='Account email whose personal reviews should be exported')
    parser.add_argument('--out', default='retroreview-static-import.json', help='Output JSON file')
    args = parser.parse_args()
    db_path = Path(args.db).expanduser().resolve()
    if not db_path.is_file():
        raise SystemExit(f'Database not found: {db_path}\nRun this script from your existing RetroReview folder or pass --db "path/to/retroreview.sqlite3".')
    con = sqlite3.connect(f'file:{db_path.as_posix()}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    tables = {r['name'] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {'generations', 'platforms', 'games', 'platform_releases', 'reviews', 'users'}
    if not required.issubset(tables):
        raise SystemExit('This database does not appear to be a RetroReview database. Missing: ' + ', '.join(sorted(required - tables)))

    users = con.execute('SELECT id,email FROM users ORDER BY email').fetchall()
    chosen = args.email
    if not chosen and users:
        print('Accounts found (only the selected account\'s reviews will be included):')
        for i, u in enumerate(users, 1): print(f'  {i}. {u["email"]}')
        raw = input('Choose account number, or press Enter to export catalogue only: ').strip()
        if raw:
            try: chosen = users[int(raw)-1]['email']
            except (ValueError, IndexError): raise SystemExit('Invalid account selection.')
    user_id = None
    if chosen:
        user = con.execute('SELECT id,email FROM users WHERE lower(email)=lower(?)', (chosen.strip(),)).fetchone()
        if not user: raise SystemExit(f'Account not found: {chosen}')
        user_id = user['id']

    generations = [dict(r) for r in con.execute('SELECT id,number,name,source_url,notes FROM generations ORDER BY number')]
    platforms = []
    for row in con.execute("SELECT p.*,g.number AS generation_number,g.name AS generation_name FROM platforms p JOIN generations g ON g.id=p.generation_id WHERE p.inclusion_status='included' ORDER BY g.number,p.name"):
        p = dict(row); p['wiki_list_pages'] = json_value(p.pop('wiki_list_pages_json', '[]'), [])
        platforms.append(p)
    game_rows = con.execute('SELECT * FROM games ORDER BY canonical_title').fetchall()
    games = []
    for row in game_rows:
        g = dict(row)
        g['title'] = g.pop('canonical_title')
        g['alternate_titles'] = json_value(g.pop('alternate_titles_json', '[]'), [])
        g['genres'] = json_value(g.pop('genres_json', '[]'), [])
        g['releases'] = []
        games.append(g)
    game_by_id = {g['id']: g for g in games}
    release_sql = '''SELECT pr.*,p.slug AS platform_slug,p.name AS platform_name,g.number AS generation_number
                     FROM platform_releases pr JOIN platforms p ON p.id=pr.platform_id
                     JOIN generations g ON g.id=p.generation_id WHERE p.inclusion_status='included'
                     ORDER BY g.number,p.name,pr.earliest_release_date'''
    for row in con.execute(release_sql):
        r = dict(row); target = game_by_id.get(r['game_id'])
        if not target: continue
        r['regions'] = json_value(r.pop('regions_json', '[]'), [])
        r.pop('source_hash', None)
        target['releases'].append(r)
    reviews = []
    if user_id is not None:
        sql = '''SELECT rv.rating,rv.review_text,rv.created_at,rv.updated_at,g.slug AS game_slug,
                        p.slug AS platform_slug
                 FROM reviews rv JOIN games g ON g.id=rv.game_id JOIN platforms p ON p.id=rv.platform_id
                 WHERE rv.user_id=? ORDER BY g.canonical_title,p.name'''
        reviews = [dict(r) for r in con.execute(sql, (user_id,))]
    con.close()
    output = {'format':'retroreview-static-v1','exportedAt':datetime.now(timezone.utc).isoformat(),
              'sourceDatabase':db_path.name,'exportedReviewAccount':chosen or None,
              'generations':generations,'platforms':platforms,'games':games,'reviews':reviews}
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Export complete: {out}')
    print(f'  Generations: {len(generations)}')
    print(f'  Platforms:   {len(platforms)}')
    print(f'  Games:       {len(games)}')
    print(f'  Releases:    {sum(len(g["releases"]) for g in games)}')
    print(f'  Reviews:     {len(reviews)}' + (f' for {chosen}' if chosen else ' (catalogue only)'))
    print('No password hashes, login sessions, or account credentials were exported.')

if __name__ == '__main__': main()
