"""Run offline with: python -m unittest -v"""
import unittest
from unittest.mock import patch

import pandas as pd

from analytics import (SPORTS, LEVELS, GROUP, load_championships, validate_championships,
                       championship_summary, coverage, load_ipl, ipl_team_summary, ipl_players)


class AnalyticsChecks(unittest.TestCase):
    def test_all_five_sports_both_levels_and_conservation(self):
        data = load_championships()
        self.assertEqual(set(zip(data.sport, data.level)), {(s, l) for s in SPORTS for l in LEVELS})
        self.assertEqual(len(data), 50)
        self.assertTrue(coverage(data).editions.eq(5).all())
        for _, subset in data.groupby(GROUP):
            summary = championship_summary(subset)
            self.assertEqual(summary.titles.sum(), len(subset))
            self.assertEqual(summary.finals.sum(), 2 * len(subset))
            self.assertAlmostEqual(summary.title_share_pct.sum(), 100)

    def test_final_conversion_is_not_season_win_rate(self):
        data = load_championships()
        sample = data[data.competition.eq('UEFA Champions League')]
        summary = championship_summary(sample).set_index('team')
        self.assertEqual(summary.loc['Real Madrid', 'titles'], 2)
        self.assertEqual(summary.loc['Real Madrid', 'title_share_pct'], 40)
        self.assertEqual(summary.loc['Manchester City', 'final_conversion_pct'], 50)
        self.assertEqual(summary.loc['Liverpool', 'titles'], 0)

    def test_invalid_uploads_fail_explicitly(self):
        data = load_championships().head(1)
        invalid = [data.drop(columns='champion'), data.iloc[:0], pd.concat([data, data])]
        for column, value in [('year', 2020.5), ('year', float('inf')), ('champion', '  '),
                              ('champion', None), ('runner_up', data.iloc[0].champion),
                              ('source_url', 'javascript:alert(1)'), ('sport', 'Unknown'),
                              ('level', 'International'), ('category', 'Unknown')]:
            invalid.append(data.assign(**{column: value}))
        for frame in invalid:
            with self.subTest(frame=frame.to_dict()), self.assertRaises(ValueError):
                validate_championships(frame)

    def test_ipl_dates_results_and_denominators(self):
        matches = load_ipl()
        self.assertEqual(len(matches), 756)
        self.assertEqual(matches.outcome.eq('No result').sum(), 4)
        self.assertEqual(matches.outcome.eq('Tiebreak decided').sum(), 9)
        self.assertEqual(str(matches.set_index('id').loc[11415, 'date'].date()), '2019-05-12')
        summary = ipl_team_summary(matches)
        self.assertEqual(summary.matches.sum(), 1512)
        self.assertEqual(summary.wins.sum(), 752)
        self.assertEqual(summary.losses.sum(), 752)
        no_results = ipl_team_summary(matches[matches.winner.isna()])
        self.assertTrue(no_results.win_pct.isna().all())
        self.assertNotIn('Delhi Daredevils', summary.team.values)
        self.assertIn('Deccan Chargers', summary.team.values)
        self.assertIn('Sunrisers Hyderabad', summary.team.values)

    def test_player_edge_cases(self):
        base = dict(match_id=1, batsman='A', non_striker='B', bowler='C', is_super_over=0,
                    batsman_runs=0, wide_runs=0, noball_runs=0, bye_runs=0, legbye_runs=0,
                    penalty_runs=0, total_runs=0, dismissal_kind=None)
        balls = pd.DataFrame([dict(base, batsman_runs=4, total_runs=4),
                              dict(base, wide_runs=1, total_runs=1),
                              dict(base, bye_runs=2, total_runs=2, dismissal_kind='run out'),
                              dict(base, dismissal_kind='bowled'),
                              dict(base, is_super_over=1, batsman_runs=6, total_runs=6)])
        with patch('analytics.pd.read_csv', side_effect=[balls, pd.DataFrame({'id': [1]})]):
            batting, bowling = ipl_players()
        self.assertEqual(batting.loc['A', 'runs'], 4)
        self.assertEqual(batting.loc['B', 'batting_appearances'], 1)
        self.assertEqual(batting.loc['B', 'runs'], 0)
        self.assertEqual(bowling.loc['C', 'wickets'], 1)
        self.assertEqual(bowling.loc['C', 'legal_balls'], 3)
        self.assertEqual(bowling.loc['C', 'economy'], 10)

    def test_app_filters_and_empty_states(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file('app.py', default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        for sport in SPORTS:
            app.selectbox[0].select(sport).run()
            self.assertEqual(len(app.exception), 0, sport)
        app.multiselect(key="levels").set_value([]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('No editions' in w.value for w in app.warning))
        app.multiselect(key="seasons").set_value([]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('Select at least one' in w.value for w in app.warning))


if __name__ == '__main__':
    unittest.main()
