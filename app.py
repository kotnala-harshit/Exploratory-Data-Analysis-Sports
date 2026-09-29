"""Run with: python -m streamlit run app.py"""
import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import (SPORTS, LEVELS, championship_summary, coverage, load_championships,
                       load_ipl, ipl_team_summary, ipl_players, validate_championships)

st.set_page_config(page_title='World Sports Observatory', page_icon='🌍', layout='wide')
st.title('World Sports Observatory')
st.markdown('Five global sports. Club and franchise teams. National teams. **Explore the evidence.**')
st.caption('Bundled historical data · Championship coverage ends at or before 2024 · IPL match data: 2008–2019')

with st.sidebar:
    st.header('Explore championships')
    sport = st.selectbox('Sport', SPORTS)
    levels = st.multiselect('Competition level', LEVELS, default=list(LEVELS), key="levels")
    uploaded = st.file_uploader('Optional replacement championship CSV', type='csv',
                               help='Uses the schema in data/README.md. Replaces the championship dataset for this session.')
    st.caption('Sport and level filters apply to the Championships tab. The IPL lab has separate season filters.')

try:
    data = validate_championships(pd.read_csv(uploaded)) if uploaded else load_championships()
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error(f'Cannot analyse this CSV: {exc}')
    st.stop()

championships, ipl, methodology = st.tabs(['Championships', 'IPL performance lab', 'Coverage & methodology'])
with championships:
    st.info('These are championship editions, not all matches. Final conversion measures titles / final appearances. '
            'The five sports are an editorial selection, not a measured global popularity ranking.')
    selected = data[data.sport.eq(sport) & data.level.isin(levels)]
    if selected.empty:
        st.warning('No editions match this sport and level selection. Select a level or upload more data.')
    else:
        low, high = int(selected.year.min()), int(selected.year.max())
        years = st.slider('Championship year range', low, high, (low, high)) if low < high else (low, high)
        selected = selected[selected.year.between(*years)]
        if selected.empty:
            st.warning('No championship editions in this year range. Try a wider range.')
        else:
            a, b, c = st.columns(3)
            a.metric('Editions in selection', len(selected))
            b.metric('Competitions', selected.competition.nunique())
            c.metric('Years represented', selected.year.nunique())
            for level, column in zip(LEVELS, st.columns(2)):
                with column:
                    st.subheader(level)
                    scoped = selected[selected.level.eq(level)]
                    if scoped.empty:
                        st.caption('No editions selected for this level.')
                        continue
                    # Keep competitions and categories separate, including in uploaded datasets.
                    for (competition, category), subset in scoped.groupby(['competition', 'category']):
                        st.markdown(f'**{competition} · {category}**')
                        st.caption(f'{len(subset)} editions · {subset.year.min()}–{subset.year.max()} · championship-only sample')
                        summary = championship_summary(subset)
                        fig = px.bar(summary.sort_values('titles'), x='titles', y='team', orientation='h',
                                     hover_data=['finals', 'final_conversion_pct', 'title_share_pct'],
                                     labels={'team': 'Team', 'titles': 'Titles in selected editions'},
                                     color_discrete_sequence=['#18b6a2'])
                        fig.update_layout(height=360, margin=dict(l=0, r=10, t=10, b=0))
                        st.plotly_chart(fig, width='stretch', key=f'{sport}/{level}/{competition}/{category}')
                        st.dataframe(summary[['team', 'titles', 'finals', 'final_conversion_pct', 'title_share_pct']].round(1),
                                     hide_index=True, width='stretch')
            st.subheader('Championship timeline & sources')
            st.dataframe(selected.sort_values('year', ascending=False), hide_index=True, width='stretch',
                         column_config={'source_url': st.column_config.LinkColumn('Source')})
            st.download_button('Download selected editions', selected.to_csv(index=False).encode(),
                               'championships_selected.csv', 'text/csv')

with ipl:
    matches = load_ipl()
    st.subheader('Twelve IPL seasons, re-examined')
    seasons = st.multiselect('IPL seasons', sorted(matches.season.unique()), default=sorted(matches.season.unique()), key="seasons")
    matches = matches[matches.season.isin(seasons)]
    if matches.empty:
        st.warning('Select at least one IPL season.')
    else:
        a, b, c = st.columns(3)
        decided = matches[matches.winner.notna()]
        a.metric('Matches', len(matches))
        b.metric('No results', matches.winner.isna().sum())
        c.metric('Toss winner also won', f'{100 * decided.toss_winner.eq(decided.winner).mean():.1f}%')
        st.caption('Toss statistic excludes no-results and is descriptive, not evidence of causation. '
                   'Tiebreak winners count as decided matches. Historical CSV is not a live feed.')
        teams = ipl_team_summary(matches)
        minimum = st.number_input('Minimum decided matches for team chart', min_value=1, value=10, step=1)
        eligible = teams[teams.decided.ge(minimum)]
        if eligible.empty:
            st.info('No teams meet this minimum; lower the threshold.')
        else:
            st.plotly_chart(px.bar(eligible.sort_values('win_pct'), x='win_pct', y='team', orientation='h',
                                  hover_data=['matches', 'wins', 'losses', 'no_result'],
                                  labels={'win_pct': 'Wins / decided matches (%)', 'team': 'Team'},
                                  color_discrete_sequence=['#18b6a2']), width='stretch')
        st.dataframe(teams.round(2), hide_index=True, width='stretch')
        a, b = st.columns(2)
        with a:
            season_counts = matches.groupby('season').size().rename('matches').reset_index()
            st.plotly_chart(px.bar(season_counts, x='season', y='matches', title='Matches per season'), width='stretch')
        with b:
            outcomes = matches.outcome.value_counts().rename_axis('outcome').reset_index(name='matches')
            st.plotly_chart(px.bar(outcomes, x='outcome', y='matches', title='How matches were resolved'), width='stretch')
        batting, bowling = ipl_players(matches.id)
        st.subheader('Player performance')
        st.caption('Super overs excluded. Batting appearances mean matches observed at the crease, not playing-XI selections. '
                   'Bowling economy uses legal deliveries and excludes byes, leg-byes, and penalty runs.')
        a, b = st.columns(2)
        with a:
            st.markdown('**Leading run scorers**')
            st.dataframe(batting.head(15), width='stretch')
        with b:
            st.markdown('**Leading wicket takers**')
            st.dataframe(bowling.head(15).round(2), width='stretch')
        st.download_button('Download IPL team analysis', teams.to_csv(index=False).encode(), 'ipl_teams.csv', 'text/csv')

with methodology:
    st.subheader('What the data can tell us')
    st.dataframe(coverage(data), hide_index=True, width='stretch')
    st.markdown('''
    - **Championships:** 50 curated historical editions in the bundled dataset, five per competition.
      Each row represents one title, including an entire NBA Finals series or Davis Cup team tie.
      It is not a fixture, player, or full-season dataset.
    - **Comparisons:** titles, final appearances, conversion, and title share stay within one
      competition and category. Raw scores across sports have different units and are not combined.
      Different year windows and tournament frequencies prevent a fair global strength ranking.
    - **Tennis:** World TeamTennis is a mixed-gender franchise competition; Davis Cup is a men's
      national-team competition. Their formats and player pools differ. All other bundled competitions are men's.
    - **IPL:** the original 756 matches and 179,078 delivery records are preserved.
      Delhi's rebrand and Pune's spelling change are unified; Deccan Chargers and Sunrisers remain separate.
      No missing results are imputed. The delivery data may contain source errors; figures describe this CSV.
    - **Limitations:** historical samples end in different years, women-only competitions are not yet included,
      and no popularity estimates, predictions, causal claims, or all-time records are inferred.
      See `data/README.md` for provenance, update rules, and licensing notes.
    ''')
