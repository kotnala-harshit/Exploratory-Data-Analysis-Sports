"""Reproducible championship and IPL analysis; no network access at runtime."""
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SPORTS = ('Football', 'Cricket', 'Basketball', 'Tennis', 'Volleyball')
LEVELS = ('Club / franchise', 'National team')
GROUP = ['sport', 'level', 'competition', 'category']
FIELDS = GROUP + ['year', 'champion', 'runner_up', 'source_url']
ALIASES = {'Delhi Daredevils': 'Delhi Capitals',
           'Rising Pune Supergiants': 'Rising Pune Supergiant'}


def validate_championships(frame):
    """Reject ambiguous or incomplete edition records instead of silently fixing them."""
    missing = set(FIELDS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    data = frame[FIELDS].copy()
    if data.empty:
        raise ValueError('The championship CSV is empty.')
    for col in set(FIELDS) - {'year'}:
        if data[col].isna().any() or not data[col].map(lambda v: isinstance(v, str)).all():
            raise ValueError(f'{col} must contain non-empty text.')
        data[col] = data[col].str.strip()
        if data[col].eq('').any():
            raise ValueError(f'{col} must contain non-empty text.')
    year = pd.to_numeric(data.year, errors='coerce')
    if not (year.between(1800, pd.Timestamp.now().year) & year.mod(1).eq(0)).all():
        raise ValueError('year must be a whole historical calendar year.')
    data['year'] = year.astype(int)
    for col, allowed in [('sport', SPORTS), ('level', LEVELS), ('category', ['Men', 'Women', 'Mixed'])]:
        if not data[col].isin(allowed).all():
            raise ValueError(f'Unknown {col}; allowed values: {allowed}')
    if data.duplicated(GROUP + ['year']).any():
        raise ValueError('Duplicate competition edition (sport/level/competition/category/year).')
    if data.champion.eq(data.runner_up).any():
        raise ValueError('Champion and runner-up must differ.')
    if not data.source_url.map(lambda u: urlparse(u).scheme == 'https' and bool(urlparse(u).hostname)).all():
        raise ValueError('Each source_url must be an HTTPS source link.')
    return data.sort_values(GROUP + ['year']).reset_index(drop=True)


def load_championships(path=None):
    return validate_championships(pd.read_csv(path or ROOT / 'data/championships.csv'))


def championship_summary(data):
    """One row per team per competition; conversion is conditional on reaching the final."""
    winners = data[GROUP + ['champion']].rename(columns={'champion': 'team'}).assign(titles=1)
    runners = data[GROUP + ['runner_up']].rename(columns={'runner_up': 'team'}).assign(titles=0)
    out = pd.concat([winners, runners]).groupby(GROUP + ['team']).agg(
        finals=('titles', 'size'), titles=('titles', 'sum')).reset_index()
    out['runner_up_finishes'] = out.finals - out.titles
    out['final_conversion_pct'] = 100 * out.titles / out.finals
    out = out.merge(data.groupby(GROUP).size().rename('editions'), on=GROUP, validate='many_to_one')
    out['title_share_pct'] = 100 * out.titles / out.editions
    return out.sort_values(['titles', 'finals', 'team'], ascending=[False, False, True]).reset_index(drop=True)


def coverage(data):
    return data.groupby(GROUP).agg(editions=('year', 'size'), first_year=('year', 'min'),
                                   last_year=('year', 'max'), unique_champions=('champion', 'nunique')).reset_index()


def load_ipl():
    data = pd.read_csv(ROOT / 'matches.csv')
    if data.id.duplicated().any():
        raise ValueError('Duplicate IPL match IDs.')
    # The original CSV mixes ISO dates with day/month/two-digit-year dates.
    data['date'] = data.date.map(lambda s: pd.to_datetime(s, format='%Y-%m-%d' if '-' in s else '%d/%m/%y'))
    for col in ['team1', 'team2', 'winner', 'toss_winner']:
        data[col] = data[col].replace(ALIASES)
    bad = data.winner.notna() & ~((data.winner == data.team1) | (data.winner == data.team2))
    if bad.any():
        raise ValueError('IPL winner must be one of the participating teams.')
    data['outcome'] = np.select(
        [data.winner.isna(), data.result.eq('tie'), data.win_by_runs.gt(0), data.win_by_wickets.gt(0)],
        ['No result', 'Tiebreak decided', 'Bat first', 'Chase'], default='Other')
    return data.sort_values('date').reset_index(drop=True)


def ipl_team_summary(data):
    rows = []
    for col in ['team1', 'team2']:
        side = data[['id', 'season', col, 'winner']].rename(columns={col: 'team'})
        side['wins'] = side.team.eq(side.winner).astype(int)
        side['decided'] = side.winner.notna().astype(int)
        rows.append(side)
    out = pd.concat(rows).groupby('team').agg(matches=('id', 'size'), wins=('wins', 'sum'),
                                            decided=('decided', 'sum')).reset_index()
    out['no_result'] = out.matches - out.decided
    out['losses'] = out.decided - out.wins
    out['win_pct'] = 100 * out.wins / out.decided.replace(0, np.nan)
    return out.sort_values(['wins', 'team'], ascending=[False, True]).reset_index(drop=True)


def ipl_players(match_ids=None):
    data = pd.read_csv(ROOT / 'deliveries.csv')
    known = pd.read_csv(ROOT / 'matches.csv', usecols=['id']).id
    if not data.match_id.isin(known).all():
        raise ValueError('A delivery refers to an unknown match.')
    data = data[data.is_super_over.eq(0)].copy()
    if match_ids is not None:
        data = data[data.match_id.isin(match_ids)].copy()
    data['four'] = data.batsman_runs.eq(4)
    data['six'] = data.batsman_runs.eq(6)
    batting = data.groupby('batsman').agg(runs=('batsman_runs', 'sum'), fours=('four', 'sum'), sixes=('six', 'sum'))
    appearances = pd.concat([
        data[['match_id', col]].rename(columns={col: 'batsman'}) for col in ['batsman', 'non_striker']
    ]).groupby('batsman').match_id.nunique().rename('batting_appearances')
    batting = appearances.to_frame().join(batting).fillna(0)
    data['credited_wicket'] = data.dismissal_kind.isin(
        ['bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket'])
    data['legal_ball'] = data.wide_runs.eq(0) & data.noball_runs.eq(0)
    data['conceded'] = data.total_runs - data.bye_runs - data.legbye_runs - data.penalty_runs
    bowling = data.groupby('bowler').agg(wickets=('credited_wicket', 'sum'), legal_balls=('legal_ball', 'sum'),
                                        runs_conceded=('conceded', 'sum'))
    bowling['economy'] = 6 * bowling.runs_conceded / bowling.legal_balls.replace(0, np.nan)
    return batting.sort_values('runs', ascending=False), bowling.sort_values('wickets', ascending=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--championships', type=Path, help='Validate and analyse a replacement championship CSV.')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports')
    args = parser.parse_args()
    championships = load_championships(args.championships)
    args.output.mkdir(parents=True, exist_ok=True)
    championship_summary(championships).to_csv(args.output / 'championship_summary.csv', index=False)
    coverage(championships).to_csv(args.output / 'coverage.csv', index=False)
    ipl_team_summary(load_ipl()).to_csv(args.output / 'ipl_teams.csv', index=False)
    batting, bowling = ipl_players()
    batting.to_csv(args.output / 'ipl_batting.csv')
    bowling.to_csv(args.output / 'ipl_bowling.csv')
    print(f'Exported 5 reports to {args.output.resolve()}')
