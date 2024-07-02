from flask import Flask, render_template, request, jsonify
import understat
import aiohttp
import asyncio

app = Flask(__name__)

async def fetch_player_stats(player_name, season):
    async with aiohttp.ClientSession() as session:
        understat_instance = understat.Understat(session)
        players = await understat_instance.get_league_players("serie_a", season)
        for player in players:
            if player['player_name'] == player_name:
                xG = float(player.get('xG', 0))
                xA = float(player.get('xA', 0))
                minutes = int(player.get('time', 0))
                key_passes = int(player.get('key_passes', 0))

                # Calcola xG90 e xA90
                xG90 = round(xG / (minutes / 90), 2) if minutes > 0 else 0
                xA90 = round(xA / (minutes / 90), 2) if minutes > 0 else 0

                # Recupera l'ID del giocatore per creare l'URL della heatmap
                player_id = player['id']
                heatmap_url = f"https://understat.com/player/{player_id}"

                return {
                    'xG': round(xG, 2),
                    'xA': round(xA, 2),
                    'games': player.get('games', 0),
                    'xG90': xG90,
                    'xA90': xA90,
                    'key_passes': key_passes,
                    'heatmap_url': heatmap_url
                }
        return None

@app.route('/')
def index():
    seasons = ["2023", "2022", "2021", "2020", "2019"]
    return render_template('index.html', seasons=seasons)

@app.route('/player_names', methods=['GET'])
async def player_names():
    season = request.args.get('season')
    if not season:
        return jsonify([])

    async with aiohttp.ClientSession() as session:
        understat_instance = understat.Understat(session)
        players = await understat_instance.get_league_players("serie_a", season)
        player_names = [player['player_name'] for player in players]
        return jsonify(player_names)

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
