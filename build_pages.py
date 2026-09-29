"""Build the public GitHub Pages dashboard from the shared analytics functions."""
import json
import shutil
from pathlib import Path

from analytics import ROOT, load_championships, load_ipl, ipl_team_summary, ipl_players


def build(output=ROOT / '_site'):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    matches = load_ipl()
    seasons = {'All seasons': matches}
    seasons.update({str(year): frame for year, frame in matches.groupby('season')})
    ipl = {}
    for label, frame in seasons.items():
        batting, bowling = ipl_players(frame.id)
        decided = frame[frame.winner.notna()]
        ipl[label] = {
            'matches': len(frame), 'no_results': int(frame.winner.isna().sum()),
            'toss_win_pct': 100 * decided.toss_winner.eq(decided.winner).mean(),
            'teams': json.loads(ipl_team_summary(frame).round(2).to_json(orient='records')),
            'batting': json.loads(batting.head(15).reset_index().to_json(orient='records')),
            'bowling': json.loads(bowling.head(15).round(2).reset_index().to_json(orient='records')),
            'outcomes': frame.outcome.value_counts().to_dict(),
        }
    data = {'championships': load_championships().to_dict('records'), 'ipl': ipl}
    (output / 'data.json').write_text(json.dumps(data, allow_nan=False), encoding='utf-8')
    for filename in ['index.html', 'dashboard.js', 'style.css']:
        shutil.copyfile(ROOT / 'pages' / filename, output / filename)
    (output / '.nojekyll').touch()
    print(f'Built public dashboard: {output}')
    return data


if __name__ == '__main__':
    build()
