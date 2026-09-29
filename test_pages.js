'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {summarize} = require('./pages/dashboard.js');
const data = JSON.parse(fs.readFileSync('_site/data.json', 'utf8'));
assert.equal(data.championships.length, 50);
const groups = new Map();
for (const row of data.championships) {
  const key = JSON.stringify([row.sport, row.level, row.competition, row.category]);
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push(row);
}
assert.equal(groups.size, 10);
for (const rows of groups.values()) {
  const ranks = summarize(rows);
  assert.equal(ranks.reduce((n, row) => n + row.titles, 0), rows.length);
  assert.equal(ranks.reduce((n, row) => n + row.finals, 0), 2 * rows.length);
  assert.ok(Math.abs(ranks.reduce((n, row) => n + row.title_share_pct, 0) - 100) < 1e-9);
}
const football = summarize(data.championships.filter(row => row.competition === 'UEFA Champions League'));
assert.equal(football.find(row => row.team === 'Real Madrid').titles, 2);
assert.equal(football.find(row => row.team === 'Manchester City').final_conversion_pct, 50);
assert.deepEqual(summarize([]), []);
assert.equal(Object.keys(data.ipl).length, 13);
assert.equal(data.ipl['All seasons'].matches, 756);
assert.equal(data.ipl['All seasons'].no_results, 4);
assert.equal(data.ipl['2013'].matches, 76);
for (const season of Object.values(data.ipl)) {
  assert.equal(season.teams.reduce((n, row) => n + row.matches, 0), 2 * season.matches);
  assert.equal(season.teams.reduce((n, row) => n + row.wins, 0), season.matches - season.no_results);
}
console.log('Pages checks passed: 10 competitions, final conversion, empty selection, 13 IPL views.');
