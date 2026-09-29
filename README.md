# World Sports Observatory

Reproducible exploratory analysis of **football, cricket, basketball, tennis, and volleyball**, covering **club/franchise and national-team competition**.

Start with the interactive explorer, follow the notebooks, or export the analysis as CSV. Everything runs offline after installation, with real historical data included.

## Included coverage

- **Football:** UEFA Champions League (2020–2024) and FIFA World Cup (2006–2022).
- **Cricket:** IPL championship editions (2015–2019) and ICC men's T20 World Cup (2014–2024), plus the original **756 IPL matches and 179,078 delivery records** from 2008–2019.
- **Basketball:** NBA (2020–2024) and FIBA men's Basketball World Cup (2006–2023).
- **Tennis:** World TeamTennis franchises (2017–2021, mixed-gender) and Davis Cup national teams (2019–2024, men).
- **Volleyball:** FIVB men's Club World Championship (2017–2022) and men's World Championship (2006–2022).

The championship dataset contains **50 editions: five per competition**, with a primary-source URL on every row. Date ranges include tournament editions, not every intervening year. This is historical championship coverage, **not full match/player coverage for all five sports or a live feed**. The five sports are an editorial selection; there is no universal, agreed global popularity ranking. Women's competitions and broader league coverage remain outside the bundled sample.

## Run locally

Python 3.11 or newer:

```bash
git clone https://github.com/kotnala-harshit/Exploratory-Data-Analysis-Sports.git
cd Exploratory-Data-Analysis-Sports
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate` instead. Streamlit displays its local address when it starts.

The explorer provides sport/level/year filters, competition-specific title and final-appearance comparisons, source links, CSV downloads, a validated replacement-data upload, and a separate IPL performance lab.

For notebooks:

```bash
jupyter notebook "Global Sports EDA.ipynb"
jupyter notebook "EDA Sports IPL Dataset.ipynb"
```

For reproducible CSV reports without opening the interface:

```bash
python analytics.py
python analytics.py --championships path/to/verified_editions.csv --output reports/custom
```

The command writes championship summaries, coverage, IPL team results, batting, and bowling reports. A replacement file affects the championship reports; IPL reports continue to use the original CSVs.

## Questions answered

1. Which teams won the most titles **within the sampled editions** of each competition?
2. Which finalists converted their appearances into titles, and how large is the denominator?
3. How concentrated are titles within each five-edition competition sample?
4. How do IPL match volumes, team win percentages, outcomes, and toss associations vary by season?
5. Who leads the supplied IPL data in runs, boundaries, and bowler-credited wickets?

Final conversion is **titles / final appearances**, not a season-wide match win rate. Title share is **titles / sampled editions in the same competition and category**. Annual club tournaments and less frequent national tournaments have different observation windows; the project does not rank their relative strength. NBA series and Davis Cup team ties each represent one championship edition. Scores with incompatible units are not pooled.

## Improvements to the original IPL notebook

- Correct mixed date formats and retain no-results rather than imputing winners.
- Distinguish run-margin wins, wicket-margin wins, tiebreak decisions, and no-results.
- Report match opportunities and win percentages alongside raw wins.
- Unify Delhi's rebrand and Pune's spelling change without merging unrelated franchises.
- Count observed batting appearances using striker and non-striker records, rather than counting dismissals as matches played.
- Exclude super overs from standard player totals; credit only qualifying dismissals to bowlers.
- Calculate bowling economy from legal deliveries, excluding byes, leg-byes, and penalties.
- Generate findings from the actual data and remove unsupported football/xG claims and finals inferred from file order.
- Share calculation code between notebooks, reports, and the explorer.

The supplied delivery data is preserved, not independently corrected against every official scorecard. Player totals describe the file and should not be presented as audited official records.

## Files

```text
app.py                           Interactive Streamlit explorer
analytics.py                     Validation, calculations, CSV export
Global Sports EDA.ipynb           Five-sport championship analysis
EDA Sports IPL Dataset.ipynb      Revised match/player analysis
data/championships.csv            50 sourced championship editions
data/README.md                    Provenance, schema, selection, limitations
matches.csv                      Original IPL match data, unchanged
deliveries.csv                   Original IPL delivery data, unchanged
test_analytics.py                Offline regression and interface checks
.github/workflows/check.yml       Tests, report generation, notebook execution
```

## Validate changes

```bash
python -m unittest -v
python analytics.py
python -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=180 *.ipynb
```

Checks cover all ten sport/level combinations, championship arithmetic, invalid uploads, IPL dates and denominators, bowling and batting edge cases, all five sport filters, and empty selections. CI repeats these checks and executes both notebooks.

## Data and reuse

See [data/README.md](data/README.md) for sources and the exact CSV contract. Source links are attribution, not a blanket licence to redistribute third-party datasets. No new licence is applied to the pre-existing IPL files. Add verified historical editions using the documented schema; no account, paid API, or scraping service is required to run the project.

**Harshit Kotnala** · [GitHub](https://github.com/kotnala-harshit) · [Portfolio](https://kotnala-harshit.github.io)
