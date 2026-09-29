# Data provenance and interpretation

## Championship editions

`championships.csv` is a manually curated factual reference dataset: **50 completed championship editions**, five for each of ten competitions. It includes winners and runners-up, not complete fixtures, scores, player statistics, or all participating teams. The snapshot deliberately stops at or before 2024; it is not the latest available season.

Sources were checked on 29–30 September 2026. Each row carries its own primary-source link:

- Football clubs: [UEFA season history](https://www.uefa.com/uefachampionsleague/history/), editions 2020, 2021, 2022, 2023, 2024.
- Football nations: [FIFA finals history](https://www.fifa.com/es/tournaments/mens/worldcup/articles/todas-las-finales-de-la-copa-mundial-de-la-fifa), editions 2006, 2010, 2014, 2018, 2022.
- Cricket franchises: IPL final reports linked per row, editions 2015, 2016, 2017, 2018, 2019. These also match original CSV IDs 576, 636, 59, 7953, 11415 respectively.
- Cricket nations: ICC final reports linked per row, T20 editions 2014, 2016, 2021, 2022, 2024.
- Basketball franchises: NBA championship reports linked per row, editions 2020, 2021, 2022, 2023, 2024. Each row represents the series winner, not one game.
- Basketball nations: [FIBA edition history](https://www.fiba.basketball/en/history/201-fiba-basketball-world-cup), editions 2006, 2010, 2014, 2019, 2023.
- Tennis franchises: [WTT historical records](https://wtt.com/wp-content/uploads/2020/06/MASTER_WTT-Teams-by-year-2019-UPDATED_061020-.pdf) for 2017–2019; WTT's final video listing and final report for 2020 and 2021. This is a historical mixed-gender team league sample.
- Tennis nations: [Davis Cup champions](https://www.daviscup.com/en/previous-champions), editions 2019, 2021, 2022, 2023, 2024. A team tie determines the title; this is not an ATP singles sample. The cancelled 2020 edition is not an observation.
- Volleyball clubs: [Volleyball World previous winners](https://en.volleyballworld.com/volleyball/competitions/club-world-championship-men/2022/competition/previous-winners), editions 2017, 2018, 2019, 2021, plus its 2022 final report. The cancelled 2020 edition is not an observation.
- Volleyball nations: [Volleyball World honours](https://en.volleyballworld.com/volleyball/competitions/men-world-championship/2022/competition/honours), editions 2006, 2010, 2014, 2018, plus its 2022 final report.

Five completed historical editions per competition provide a small, equally sized starting sample. Observation periods differ: an annual league and a World Cup do not represent equal elapsed time or equal qualification difficulty. These selections are not a census of sport or a statistical sample of all professional teams.

## CSV contract

Required header:

```csv
sport,level,competition,category,year,champion,runner_up,source_url
```

- `sport`: Football, Cricket, Basketball, Tennis, or Volleyball.
- `level`: exactly `Club / franchise` or `National team`.
- `competition`: non-empty competition name; keep distinct formats and tournaments separate.
- `category`: `Men`, `Women`, or `Mixed`. The bundled file contains Men and Mixed only.
- `year`: whole calendar year when the championship was awarded, not a season start year.
- `champion`, `runner_up`: distinct non-empty team names, consistently spelled within a competition.
- `source_url`: an HTTPS evidence link. Validation checks URL structure; it does not fetch or verify the page automatically.

One unique row per `(sport, level, competition, category, year)`. Multiple editions in one year require distinct competition labels. Shared titles and editions without a runner-up are unsupported; do not invent a runner-up. Blank required values, unknown enums, fractional/future years, invalid links, and duplicate editions fail validation. Additional columns are ignored.

Team identity choices: Bayern Munich and Inter Milan use familiar English names; FIBA country codes are expanded; sponsor variants of Trentino and Perugia are consolidated. Cucine Lube Civitanova and Sada Cruzeiro use consistent names. The 2021 Davis Cup entry remains **Russian Tennis Federation**, matching its representation in that edition. These are editorial mappings, not fuzzy matching at load time.

## Extending coverage

1. Check the governing body's result, confirm both finalists and the winner, and record its URL.
2. Append a row using consistent team spelling and the correct category. Update coverage notes if the sample design changes.
3. Run `python -m unittest -v` and `python analytics.py`. The bundled-data test intentionally checks 50 editions and must be updated when that dataset expands.
4. Re-execute notebooks so saved outputs agree with the data. Alternatively, upload a replacement CSV in the explorer or pass `--championships` to the CLI without changing the bundled sample.

Full fixture or player expansion requires separate source data and sport-specific measures. This championship schema cannot support home advantage, form, possession, xG, player efficiency, or full-season win percentages.

## Original IPL files

`matches.csv` and `deliveries.csv` remain byte-for-byte unchanged from repository commit `629c2fce27bb925a64fccafa2990d893dd50f4c5`. The original notebook attributed the dataset through a shortened link; an explicit upstream data licence was not supplied. We do not infer or replace that licence.

There are 756 match records (2008–2019) and 179,078 delivery records, including super overs. Dates mix ISO and day/month/year formats. Four matches have no winner; nine rows have a tied regulation result followed by a winner. Those nine count as decided games but remain separate in the outcome chart.

Delhi Daredevils maps to Delhi Capitals and Rising Pune Supergiants to Rising Pune Supergiant. Deccan Chargers and Sunrisers Hyderabad remain separate. Player names are unchanged. Rows are not deduplicated using over/ball coordinates because illegal deliveries may repeat those coordinates. Missing results are never imputed.

Batting appearances count distinct matches with an observed striker or non-striker record, not squad selections. Player statistics exclude super overs. Bowler wickets include bowled, caught, caught and bowled, lbw, stumped, and hit wicket. Economy excludes byes, leg-byes, and penalty runs from conceded runs; wides and no-balls are excluded from legal-ball counts. Data errors may remain; totals describe this snapshot rather than guaranteed official records.

## Rights and limitations

The new file transcribes a small set of factual results and links to their sources; it does not reproduce articles, logos, or source databases. Third-party source terms continue to apply. No blanket open-data licence is asserted for external sources or the original IPL files. No synthetic scores, popularity estimates, predicted winners, or fabricated missing seasons are included.
