from flask import Flask, render_template, request, jsonify
import understat
import aiohttp
import asyncio

app = Flask(__name__)

async def fetch_player_stats(player_name, season):
    leagues = ["Serie_A", "Ligue_1", "Bundesliga", "EPL", "La_Liga"]
    async with aiohttp.ClientSession() as session:
        understat_instance = understat.Understat(session)
        player_data = []

        for league in leagues:
            players = await understat_instance.get_league_players(league, season)
            for player in players:
                if player['player_name'] == player_name:
                    player['league'] = league
                    player_data.append(player)

        if not player_data:
            return None

        player_data.sort(key=lambda x: int(x.get('games', 0)), reverse=True)
        player = player_data[0]

        xG = float(player.get('xG', 0))
        xA = float(player.get('xA', 0))
        minutes = int(player.get('time', 0))
        key_passes = int(player.get('key_passes', 0))
        goals = int(player.get('goals', 0))
        assists = int(player.get('assists', 0))

        xG90 = round(xG / (minutes / 90), 2) if minutes > 0 else 0
        xA90 = round(xA / (minutes / 90), 2) if minutes > 0 else 0

        player_id = player['id']
        heatmap_url = f"https://understat.com/player/{player_id}"

        return {
            'xG': round(xG, 2),
            'xA': round(xA, 2),
            'games': player.get('games', 0),
            'minutes': minutes,
            'xG90': xG90,
            'xA90': xA90,
            'key_passes': key_passes,
            'goals': goals,
            'assists': assists,
            'heatmap_url': heatmap_url,
            'league': player['league']
        }

@app.route('/')
def index():
    seasons = ["2023", "2022", "2021", "2020", "2019"]
    return render_template('index.html', seasons=seasons, default_season="2023")

@app.route('/player_names', methods=['GET'])
async def player_names():
    season = request.args.get('season')
    if not season:
        return jsonify([])

    leagues = ["Serie_A", "Ligue_1", "Bundesliga", "EPL", "La_Liga"]
    all_player_names = []

    async with aiohttp.ClientSession() as session:
        understat_instance = understat.Understat(session)
        for league in leagues:
            players = await understat_instance.get_league_players(league, season)
            for player in players:
                all_player_names.append(player['player_name'])
    
    unique_player_names = list(set(all_player_names))
    return jsonify(unique_player_names)

@app.route('/result', methods=['POST'])
def result():
    player_name = request.form['player_name']
    season = request.form['season']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    player_stats = loop.run_until_complete(fetch_player_stats(player_name, season))

    if player_stats is None:
        return "Player not found", 404

    return render_template('result.html', player_name=player_name, stats=player_stats)

if __name__ == '__main__':
    app.run(debug=True)
