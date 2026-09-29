'use strict';

function summarize(rows) {
  const teams = new Map();
  for (const row of rows) {
    for (const [team, win] of [[row.champion, 1], [row.runner_up, 0]]) {
      if (!teams.has(team)) teams.set(team, {team, titles: 0, finals: 0});
      const result = teams.get(team);
      result.titles += win;
      result.finals += 1;
    }
  }
  return [...teams.values()].map(team => ({...team,
    final_conversion_pct: 100 * team.titles / team.finals,
    title_share_pct: 100 * team.titles / rows.length
  })).sort((a, b) => b.titles - a.titles || b.finals - a.finals || a.team.localeCompare(b.team));
}

if (typeof module !== 'undefined') module.exports = {summarize};

if (typeof document !== 'undefined') {
  const $ = id => document.getElementById(id);
  const escape = value => String(value ?? '—').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const number = value => value == null ? '—' : Number.isInteger(value) ? value.toLocaleString() : value.toFixed(1);
  let data, selected = [];
  let currentView = 'championships';
  function table(rows, columns) {
    return '<div class="table-scroll"><table><thead><tr>' + columns.map(([, label]) => `<th scope="col">${escape(label)}</th>`).join('') +
      '</tr></thead><tbody>' + rows.map(row => '<tr>' + columns.map(([key]) => `<td>${escape(typeof row[key] === 'number' ? number(row[key]) : row[key])}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>';
  }
  function bars(rows, key, maximum, suffix = '') {
    return '<div class="bars">' + rows.map(row => `<div><div class="bar-top"><span>${escape(row.team)}</span><strong>${escape(number(row[key]))}${suffix}</strong></div><div class="track" aria-hidden="true"><div class="fill" style="width:${Math.max(0, Math.min(100, 100 * (row[key] || 0) / maximum))}%"></div></div></div>`).join('') + '</div>';
  }
  function metrics(id, values) {
    $(id).innerHTML = values.map(([label, value]) => `<div class="metric"><span>${escape(label)}</span><strong>${escape(value)}</strong></div>`).join('');
  }
  function championshipYears() {
    const years = [...new Set(data.championships.filter(row => row.sport === $('sport').value).map(row => row.year))].sort((a, b) => a - b);
    for (const id of ['start', 'end']) $(id).innerHTML = years.map(year => `<option>${year}</option>`).join('');
    $('end').value = years[years.length - 1];
    renderChampionships();
  }
  function renderChampionships() {
    selected = data.championships.filter(row => row.sport === $('sport').value &&
      ($('level').value === 'both' || row.level === $('level').value) && row.year >= Number($('start').value) && row.year <= Number($('end').value));
    metrics('metrics', [['Selected editions', selected.length], ['Competitions', new Set(selected.map(row => row.competition)).size], ['Years represented', new Set(selected.map(row => row.year)).size]]);
    $('download').disabled = !selected.length;
    if (!selected.length) {
      $('rankings').innerHTML = '<p class="empty">No editions match these filters. Choose a wider year range or another level.</p>';
      $('timeline').innerHTML = '';
      return;
    }
    const groups = new Map();
    for (const row of selected) {
      const key = JSON.stringify([row.level, row.competition, row.category]);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(row);
    }
    $('rankings').innerHTML = [...groups.values()].map(rows => {
      const first = rows[0], ranks = summarize(rows);
      return `<section class="panel"><p class="eyebrow">${escape(first.level)}</p><h3>${escape(first.competition)}</h3><p class="subtle">${escape(first.category)} · ${rows.length} editions · ${Math.min(...rows.map(r => r.year))}–${Math.max(...rows.map(r => r.year))}</p>` +
        bars(ranks, 'titles', Math.max(1, ...ranks.map(r => r.titles))) +
        table(ranks, [['team', 'Team'], ['titles', 'Titles'], ['finals', 'Finals'], ['final_conversion_pct', 'Final conversion %'], ['title_share_pct', 'Title share %']]) + '</section>';
    }).join('');
    const ordered = [...selected].sort((a, b) => b.year - a.year);
    $('timeline').innerHTML = '<div class="table-scroll"><table><thead><tr><th scope="col">Year</th><th scope="col">Competition</th><th scope="col">Champion</th><th scope="col">Runner-up</th><th scope="col">Source</th></tr></thead><tbody>' + ordered.map(row => `<tr><td>${row.year}</td><td>${escape(row.competition)}</td><td>${escape(row.champion)}</td><td>${escape(row.runner_up)}</td><td><a href="${escape(row.source_url)}" target="_blank" rel="noopener noreferrer" aria-label="Source for ${escape(row.competition)} ${row.year}">Verify ↗</a></td></tr>`).join('') + '</tbody></table></div>';
  }
  function renderIPL() {
    const frame = data.ipl[$('season').value];
    metrics('ipl-metrics', [['Matches', number(frame.matches)], ['No results', frame.no_results], ['Toss winner also won', number(frame.toss_win_pct) + '%']]);
    $('ipl-chart').innerHTML = bars([...frame.teams].sort((a, b) => b.win_pct - a.win_pct), 'win_pct', 100, '%');
    const outcomes = Object.entries(frame.outcomes).map(([team, count]) => ({team, count}));
    $('outcomes').innerHTML = bars(outcomes, 'count', Math.max(...outcomes.map(row => row.count)));
    $('teams').innerHTML = table(frame.teams, [['team', 'Team'], ['matches', 'Matches'], ['wins', 'Wins'], ['losses', 'Losses'], ['no_result', 'No result'], ['win_pct', 'Win %']]);
    $('batting').innerHTML = table(frame.batting, [['batsman', 'Player'], ['runs', 'Runs'], ['batting_appearances', 'Batting appearances'], ['fours', 'Fours'], ['sixes', 'Sixes']]);
    $('bowling').innerHTML = table(frame.bowling, [['bowler', 'Player'], ['wickets', 'Wickets'], ['legal_balls', 'Legal balls'], ['economy', 'Economy']]);
  }
  for (const button of document.querySelectorAll('[data-view]')) button.addEventListener('click', () => {
    currentView = button.dataset.view;
    for (const view of document.querySelectorAll('.view')) view.hidden = view.id !== currentView || !data;
    for (const other of document.querySelectorAll('[data-view]')) other.setAttribute('aria-pressed', String(other === button));
  });
  $('sport').addEventListener('change', () => { if (data) championshipYears(); });
  for (const id of ['level', 'start', 'end']) $(id).addEventListener('change', () => { if (data) renderChampionships(); });
  $('season').addEventListener('change', () => { if (data) renderIPL(); });
  $('download').addEventListener('click', () => {
    if (!selected.length) return;
    const keys = Object.keys(selected[0]);
    const csv = [keys, ...selected.map(row => keys.map(key => row[key]))].map(row => row.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = 'sports-championships.csv'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  fetch('data.json').then(response => {
    if (!response.ok) throw new Error('Data request failed');
    return response.json();
  }).then(result => {
    data = result;
    $('season').innerHTML = ['All seasons', ...Object.keys(data.ipl).filter(key => key !== 'All seasons').sort()].map(label => `<option>${escape(label)}</option>`).join('');
    championshipYears(); renderIPL();
    $('status').hidden = true;
    $(currentView).hidden = false;
  }).catch(() => {
    $('status').textContent = 'The data could not be loaded. Please reload the page, or open the source data on GitHub.';
  });
}
