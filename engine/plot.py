import os
import sys
import math
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from coloraide import Color

print('Plotting...')

DIR = sys.argv[1].replace('/calibration', '')

N_COLORS = 10
LINE_STYLES = ['solid', 'dashed', 'dashdot', 'dotted']

calib_dir = os.path.join(DIR, 'calibration')
df = pd.read_csv(os.path.join(calib_dir, '0.csv'))

report = json.load(open(os.path.join(calib_dir, '0.json')))

plots_dir = os.path.join(DIR, 'plots')
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

ranges = {
    'Temperature': {
        'min': 0,
        'max': 5
    },
    'Sea Level Rise': {
        'min': 0,
    },
    'Habitability': {
        'min': 0,
        'max': 15
    },
    'World Outlook': {
        'min': 0,
        'max': 50
    },
    'CO2 Emissions (Gt)': {
        'min': -25,
    },
    'CO2eq Emissions': {
        'min': -25,
    },
    'Fuel (TWh)': {
        'min': 0,
    },
    'Electricity (TWh)': {
        'min': 0,
    },
    'Plant Calories (Tcals)': {
        'min': 0,
    },
    'Animal Calories (Tcals)': {
        'min': 0,
    },
    'Land': {
        'min': 0,
    },
    'Extinction Rate': {
        'min': 0,
        'max': 100
    },
    'Cal per Capita per Day': {
        'min': 0,
        'max': 4000,
    }
}

groups = {
    'General': [
        'Population (b)', 'Temperature', 'Habitability',
        'Extinction Rate', 'Sea Level Rise', 'Mean Income Level'],
    'Emissions': [
        'CO2eq Emissions', 'CO2 Emissions (Gt)',
        'CH4 Emissions (Mt)', 'N2O Emissions (Mt)'],
    'Production': [
        'Demand & Consumed', 'Cal per Capita per Day',
        'Fuel (TWh)', 'Electricity (TWh)',
        'Animal Calories (Tcals)', 'Plant Calories (Tcals)',
        'Water', 'Land',
    ],
    'Electricity': ['Electricity (TWh)'],
    'Fuel': ['Fuel (TWh)'],
    'PlantCalories': ['Plant Calories (Tcals)'],
    'AnimalCalories': ['Animal Calories (Tcals)'],
    'Outlook': ['World Outlook'],
    'Events': ['Events', ],
}

plots = {
    'Population (b)': ['Population (b)', 'Pop Ref (2100, bn people)'],
    'Events': ['Events'],
    'Temperature': ['Temperature'],
    'World Outlook': ['World Outlook'],
    'Habitability': ['Habitability'],
    'Extinction Rate': ['Extinction Rate'],
    'Sea Level Rise': ['Sea Level Rise'],
    'CO2eq Emissions': [
        'CO2eq Emissions',
        'CO2eq Ref (Gt)',
    ],
    'CO2 Emissions (Gt)': [
        'CO2 Emissions (Gt)',
        'Energy CO2 Emissions (Gt)',
        'Calorie CO2 Emissions (Gt)',
        'Industry CO2 Emissions (Gt)',
        'CO2 Ref (Gt)',
    ],
    'CH4 Emissions (Mt)': [
        'CH4 Emissions (Mt)',
        'Energy CH4 Emissions (Mt)',
        'Calorie CH4 Emissions (Mt)',
        'Industry CH4 Emissions (Mt)',
        'CH4 Ref (Mt)',
    ],
    'N2O Emissions (Mt)': [
        'N2O Emissions (Mt)',
        'Energy N2O Emissions (Mt)',
        'Calorie N2O Emissions (Mt)',
        'Industry N2O Emissions (Mt)',
        'N2O Ref (Mt)',
    ],
    'Fuel (TWh)': [
        'Industry Fuel Demand (TWh)',
        'Agg Fuel Demand (TWh)',
        'Produced Fuel (TWh)',
        'Fuel Ref (TWh)',
    ],
    'Electricity (TWh)': [
        'Industry Elec Demand (TWh)',
        'Agg Elec Demand (TWh)',
        'Produced Elec (TWh)',
        'Elec Ref (TWh)',
    ],
    'Animal Calories (Tcals)': [
        'Base Animal Cal Demand (Tcals)',
        'Agg Animal Cal Demand (Tcals)',
        'Produced Animal Cals (Tcals)',
    ],
    'Plant Calories (Tcals)': [
       'Base Plant Cal Demand (Tcals)',
       'Agg Plant Cal Demand (Tcals)',
       'Produced Plant Cals (Tcals)',
    ],
    'Demand & Consumed': [
       'Produced Fuel (% Demand)',
       'Produced Elec (% Demand)',
       'Produced Animal Cals (% Demand)',
       'Produced Plant Cals (% Demand)',
       'Consumed Water (%)',
       'Consumed Land (%)',
    ],
    'Water': [
       'Energy Water Req. (km3)',
       'Calorie Water Req. (km3)',
       'Industry Water Demand (km3)',
       'Water Ref (km3)',
    ],
    'Land': [
       'Energy Land Req. (km2)',
       'Calorie Land Req. (km2)',
       'Cals Land Ref (km2)',
    ],
    'Cal per Capita per Day': [
        'Cal/Capita/Day',
        'Cals Ref (kcal/person/day)'
    ],
    'Mean Income Level': [
        'Mean Income Level'
    ],
}

icon_event_groups = {
    'Flooding': [
        'Flooding', 'Severe Flooding', 'Extreme Flooding',
    ],
    'Storms': [
        'Severe Hurricane',
        'Large Derecho Storm'
    ],
    'Wildfires': [
        'Wildfires', 'Severe Wildfires',
    ],
    'Social Unrest': ['Protests', 'Riots', 'Revolts'],
    'Heatwaves': ['Heatwaves'],
    'Crop Failures': ['Crop Failures'],
    'Disease Outbreak': ['Disease Outbreak'],
    'Attacks': ['Doom Cult Attacks'],
}

region_groups = {
    'Asia': [
        'Central Asia',
        'Eastern Asia',
        'South-eastern Asia',
        'Southern Asia',
        'Western Asia',
    ],
    'Africa': [
        'Eastern Africa',
        'Central Africa',
        'Northern Africa',
        'Southern Africa',
        'Southern Asia',
    ],
    'Europe & Neo-Europe': [
        'Eastern Europe',
        'Northern Europe',
        'Southern Europe',
        'Western Europe',
        'Northern America',
        'Australasia',
    ],
    'Americas & Islands': [
        'Central America',
        'Southern America',
        'Caribbean',
        'Oceania',
    ],
}


outputs = ['Electricity', 'Fuel', 'PlantCalories', 'AnimalCalories']
process_cols_by_output = defaultdict(lambda: defaultdict(list))
feedstock_plots = []
for col in df.columns:
    if col.startswith('Feedstock:'):
        title = col.replace(':', '-')
        feedstock_plots.append(title)
        plots[title] = [col]
        ranges[title] = {'min': 0}
    else:
        for o in outputs:
            if col.startswith('{}:'.format(o)):
                _, process, category = col.split(':')
                process_cols_by_output[o][category].append(col)
groups['Feedstocks'] = feedstock_plots

for output, categories in process_cols_by_output.items():
    for category, cols in categories.items():
        name = 'Process-{}-{}'.format(output, category)
        plots[name] = cols
        groups[output].append(name)
        if category == 'Mix Share':
            ranges[name] = {'min': 0, 'max': 1}

all_icon_events = set()
icon_event_history = report.pop('icon_events')
for evs in icon_event_history:
    for name, _ in evs:
        all_icon_events.add(name)

icon_events_by_year = {}
icon_events_by_year_output = {}
for i, icon_events in enumerate(icon_event_history):
    year = report['start_year'] + i
    counts = defaultdict(int)
    for ev, region in icon_events:
        counts[ev] += 1
        all_icon_events.add(ev)

    evs = []
    for name, count in counts.items():
        evs.append('{}x {}'.format(count, name))
    icon_events_by_year_output[year] = '<br />'.join(evs)
    icon_events_by_year[year] = {k: counts[k] for k in all_icon_events}
icon_events_df = pd.DataFrame.from_dict(icon_events_by_year, orient='index')
df = df.set_index('Year').join(icon_events_df)

for title, cols in icon_event_groups.items():
    plots[title] = cols
    groups['Events'].append(title)

for title, cols in region_groups.items():
    plots[title] = ['Outlook:{}'.format(col) for col in cols]
    groups['Outlook'].append(title)
    ranges[title] = {
        'min': 0,
        'max': 20
    }

files = {}
for group, titles in groups.items():
    files[group] = []
    for title in titles:
        cols = plots[title]
        plt.title(title)
        plt.margins(0)
        plt.xlim(report['start_year'], report['start_year']+100)

        for i, col in enumerate(cols):
            try:
                vals = df[col]
            except KeyError:
                print('Missing column:', col)
                continue
            linestyle = math.floor(i/N_COLORS)
            if title == 'Events':
                plt.scatter(df.index, vals, label=col, s=2)
            else:
                plt.plot(df.index, vals, label=col, linestyle=LINE_STYLES[linestyle])
        plt.legend(fontsize=6)

        rng = ranges.get(title, {})
        plt.ylim(bottom=rng.get('min'), top=rng.get('max'))

        ax = plt.gca()
        n_years = 100
        ax_width = ax.get_window_extent().width
        year_width = ax_width/n_years
        fig = plt.gcf()
        fig_width, fig_height = fig.get_size_inches() * fig.dpi
        ax_fig_width_ratio = ax_width/fig_width
        # print(ax_fig_width_ratio)
        # import ipdb; ipdb.set_trace()

        fname = '{}.png'.format(title)
        plt.savefig(os.path.join(plots_dir, fname))

        plt.close()
        files[group].append(fname)


events = []
events_by_year = {}
for i, evs in enumerate(report.pop('events')):
    year = report['start_year'] + i
    subevs = []
    for ev, region in evs:
        ev_name = ev if region is None else '{} in {}'.format(ev, region)
        subevs.append(ev_name)
    events_by_year[year] = subevs
    events.append((
        year,
        '<br />'.join(subevs)
    ))

report['scenarios'] = ','.join(report['scenarios'])

style = '''
* {
    box-sizing: border-box;
}
body {
    margin: 0;
}
main {
    display: flex;
}
main > div {
    padding: 1em;
}
.group {
    flex: 1;
    height: 100vh;
    overflow-y:scroll;
}
.chart-group {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-evenly;
    display: none;
}
img {
    width: 480px;
}
.meta {
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 10;
}
.tag {
    border: 1px solid;
    border-radius: 0.2em;
    display: inline-flex;
    background: #fff;
}
.tag > div:first-child {
    background: #333;
    color: #fff;
}
.tag > div {
    padding: 0 0.25em;
}
.events {
    width: 210px;
    height: 100vh;
    overflow-y:scroll;
}
.event {
    display: flex;
}
.event .year {
    margin-right: 0.5em;
}
.no-events .year {
    color: #bbb;
}
.icon-events {
    font-size: 0.7em;
    color: #777;
}

.line {
    top: 0;
    height: 100%;
    display: flex;
    font-size: 0.9em;
    border-left: 1px solid #000;
    position: absolute;
    flex-direction: column;
    justify-content: space-around;
    pointer-events: none;
    padding-left: 0.25em;
    display: none;
}

.chart-group-tabs {
    display: flex;
    justify-content: space-evenly;
    margin: 0.5em 0;
}
.chart-group-tabs > div {
    border: 1px solid;
    border-radius: 0.2em;
    padding: 0 0.2em;
    cursor: pointer;
    background: #fff;
}
.chart-group-tabs > div.selected {
    background: #333;
    color: #fff;
}

.events-meta {
    margin-top: 1em;
}
.event-encounters {
    margin: 2em 0 1em 0;
    text-align: center;
}
.event-runs {
    display: flex;
    width: 100%;
    height: 100vh;
    overflow: scroll;
}
.event-runs li {
	list-style-type: none;
}
.event-run-column > div {
    height: 120px;
    width: 220px;
    padding: 0.5em;
    border-bottom: 1px solid;
    font-size: 0.8em;
}

.run {
    border-right: 1px solid;
}
.run:nth-child(2n+1) {
	background: #f0f0f0;
}
.run-summary {
	font-size: 0.75em;
    background: rgba(0,0,0,0.1);
	border-radius: 0.2em;
    display: flex;
    padding: 0 0.25em;
    justify-content: space-between;
    margin-bottom: 0.25em;
}
.years {
    position: sticky;
    left: 0;
}
.years > div {
	width: auto;
	font-weight: bold;
	font-size: 2em;
	background: #eee;
	border-right: 4px solid black;
    display: flex;
    align-items: center;
}
.event-counts {
    padding: 1em;
    border-bottom: 4px solid;
}
.event-charts {
    padding: 1em;
    border-bottom: 4px solid;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
}
.event-counts > li {
	font-size: 0.8em;
	background: #222;
	color: #fff;
	list-style-type: none;
	margin: 0;
	line-height: 1;
	border-radius: 0.2em;
    border: 1px solid #060606;
    display: inline-block;
}
.event-pill-top {
	display: inline-flex;
    align-items: center;
}
.event-pill-top > div {
    padding: 0.25em;
}
.event-pill-top > div:last-child {
	margin: 0.1em 0.1em 0.1em 0.25em;
	border-radius: 0.2em;
	font-size: 0.85em;
	padding: 0.1em 0.1em 0;
	height: 14px;
}
.event-year-range {
    display: flex;
    align-items: center;
    font-size: 0.8em;
    padding: 0.2em;
}
.dist {
    display: flex;
    flex: 1;
    margin: 0 2px;
    overflow: hidden;
    border-radius: 0.1em;
}
.dist > div {
    height: 10px;
    flex: 1;
}
'''

tag = '''
<div class="tag">
    <div>{k}</div>
    <div>{v}</div>
</div>
'''

event = '''
<div class="event {cls}">
    <div class="year">{year}</div>
    <div>
        <div>{events}</div>
        <div class="icon-events">{icon_events}</div>
    </div>
</div>
'''

scripts = '''
<script>
const chartGroups = [...document.querySelectorAll('.chart-group')];
const chartTabs = [...document.querySelectorAll('.chart-group-tabs > div')];
chartTabs.forEach((el, i) => {
    el.addEventListener('click', () => {
        let sel = document.querySelector('.chart-group-tabs .selected');
        if (sel) sel.classList.remove('selected');
        el.classList.add('selected');
        chartGroups.forEach((g, j) => {
            if (i == j) {
                g.style.display = 'flex';
            } else {
                g.style.display = 'none';
            }
        });
    });
});
chartTabs[0].click();

[...document.querySelectorAll('.charts img')].forEach((el) => {
    el.parentElement.style.position = 'relative';

    let lineEl = document.createElement('div');
    lineEl.classList.add('line');
    el.parentElement.appendChild(lineEl);

    el.addEventListener('mousemove', (ev) => {
        let width = el.width;
        let axes_width = el.width * 0.775;
        lineEl.style.display = 'flex';
        let rect = ev.target.getBoundingClientRect();
        let x = ev.clientX - rect.left - (el.width * 0.125);
        let y = ev.clientY - rect.top;
        let i = x/axes_width;
        let year = 2022 + Math.floor(i*100);
        let events = EVENTS_BY_YEAR[year] || [];

        lineEl.style.left = `${x + (el.width * 0.125)}px`;
        lineEl.innerHTML = `<div>
            <u>${year}</u><br />
            ${events.join('<br />')}
        </div>`;
    });
    el.addEventListener('mouseleave', () => {
        lineEl.style.display = 'none';
    });
});
</script>
'''

html = '''
<html>
<head>
    <title>Half Earth Calibration</title>
    <style>{style}</style>
</head>
<body>
<main>
    <div class="group">
        <div class="meta">
            <div>{meta}</div>
            <div class="chart-group-tabs">{group_tabs}</div>
        </div>
        <div class="charts">{chart_groups}</div>
    </div>
    <div class="events">{events}</div>
</main>
<script>
const EVENTS_BY_YEAR = {events_by_year};
</script>
{scripts}
</body>
</html>
'''.format(
        style=style,
        scripts=scripts,
        events_by_year=json.dumps(events_by_year),
        meta='\n'.join(tag.format(k=k, v=v) for k, v in report.items() if k != 'summary'),
        group_tabs='\n'.join('<div>{}</div>'.format(g) for g in groups.keys()),
        chart_groups='\n'.join(
            '<div class="chart-group">{}</div>'.format('\n'.join('<div><img src="{}"></div>'.format(fname) for fname in fnames))
            for fnames in files.values()),
        events='\n'.join(
            event.format(
                year=year, events=evs,
                icon_events=icon_events_by_year_output[year],
                cls='no-events' if not evs else '')
            for year, evs in events))

with open(os.path.join(plots_dir, 'index.html'), 'w') as f:
    f.write(html)

# Event calibration
n_runs = 0
all_events = []
run_events_html = []
comparison_charts = defaultdict(list)
event_dists = defaultdict(lambda: defaultdict(int))
for runfile in os.listdir(calib_dir):
    if not runfile.endswith('.json'): continue
    if runfile == 'all_events.json': continue
    n_runs += 1
    run_data = json.load(open(os.path.join(calib_dir, runfile)))
    run_events_html.append([])
    var_trajectories = defaultdict(list)
    for i, year in enumerate(run_data['events']):
        evs = [ev for ev, _ in year]
        for ev in evs:
            event_dists[ev][report['start_year'] + i] += 1
        all_events += evs
        evs_htmls = ['<li>{}</li>'.format(ev) for ev in evs]
        for key, val in run_data['summary'][i].items():
            var_trajectories[key].append(val)
        snapshot = run_data['summary'][i]
        snapshot = '<div>🌡️{temp:.1f}</div> <div>☁️{emissions:.1f}</div> <div>🙂{outlook:.1f}</div> <div>💀{extinction_rate:.1f}</div> <div>🏠{habitability:.1f}</div> <div>🏞️{land_use:.1f}</div>'.format(**snapshot)
        run_events_html[-1].append(
                '<div><div class="run-summary">{}</div>{}</div>'.format(snapshot, '\n'.join(evs_htmls)))
    for key, val in var_trajectories.items():
        comparison_charts[key].append(val)

runs_charts = []
for key, runs in comparison_charts.items():
    plt.title(key)
    plt.margins(0)
    plt.xlim(report['start_year'], report['start_year']+100)
    years = list(range(report['start_year'], report['start_year']+100))
    for run in runs:
        plt.plot(years, run)
    fname = 'runs__{}.png'.format(key)
    plt.savefig(os.path.join(plots_dir, fname))
    plt.close()
    runs_charts.append(fname)

all_events = Counter(all_events)
total_possible_events = len(json.load(open(os.path.join(calib_dir, 'all_events.json'))))

colors = Color('red').interpolate('green', space='lch')
dist_color = Color('white').interpolate('#1567eb', space='lch')

event_dist_info = {}
for ev, dist in event_dists.items():
    min_year = min(dist.keys())
    max_year = max(dist.keys())
    total = sum(dist.values())
    max_count = max(dist.values())
    event_dist_info[ev] = {
        'min_year': min_year,
        'max_year': max_year,
        'dist': ['<div style="background:{};"></div>'.format(
            # dist_color(dist.get(min_year+i, 0)/total).to_string()) for i in range(max_year-min_year+1)]
            dist_color(dist.get(min_year+i, 0)/max_count).to_string()) for i in range(max_year-min_year+1)]
    }

html = '''
<html>
<head>
    <title>Half Earth Calibration</title>
    <style>{style}</style>
</head>
<body>
    <div class="events-meta meta">
        <div>{meta}</div>
    </div>
    <div class="event-counts">
        {counts}
        <div class="event-encounters">{count} out of {total} events occurred at least once.</div>
    </div>
    <div class="event-charts">{charts}</div>
    <div class="event-runs">{years}{runs}</div>
</body>
</html>
'''.format(
        style=style,
        count=len(all_events),
        total=total_possible_events,
        meta='\n'.join(tag.format(k=k, v=v) for k, v in report.items() if k != 'summary'),
        years='<div class="years event-run-column">{}</div>'.format('\n'.join('<div>{}</div>'.format(report['start_year'] + i) for i in range(100))),
        charts='\n'.join('<div><img src="{}"></div>'.format(fname) for fname in runs_charts),
        runs='\n'.join(['<div class="run event-run-column">{}</div>'.format('\n'.join(run)) for run in run_events_html]),
        counts='\n'.join([
            '''<li>
                <div class="event-pill-top">
                    <div>{name}</div>
                    <div style="background:{color};">{percent:.1f}%</div>
                </div>
                <div class="event-year-range">
                    <div>{min_year}</div><div class="dist">{dist}</div><div>{max_year}</div>
                </div>
            </li>'''.format(
                name=ev,
                color=colors(count/n_runs).to_string(),
                percent=count/n_runs * 100,
                min_year=event_dist_info[ev]['min_year'],
                max_year=event_dist_info[ev]['max_year'],
                dist=''.join(event_dist_info[ev]['dist']))
            for ev, count in all_events.most_common()])
    )

with open(os.path.join(plots_dir, 'events.html'), 'w') as f:
    f.write(html)