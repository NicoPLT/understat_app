from flask import Flask, render_template, request, jsonify
import understat
import asyncio
import aiohttp

app = Flask(__name__, static_url_path='/static')

async def get_league_players(season):
    async with aiohttp.ClientSession() as session:
        understat_api = understat.Understat(session)
        players = await understat_api.get_league_players("serie_a", season)
        return players

@app.route('/player_names', methods=['GET'])
async def player_names():
    season = request.args.get('season', '2023')
    players = await get_league_players(season)
    player_names = [player['player_name'] for player in players]
    return jsonify(player_names)

async def get_player_stats(player_name, season):
    players = await get_league_players(season)
    
    for player in players:
        if player['player_name'] == player_name:
            stats = {
                'xG': round(float(player['xG']), 2),
                'xA': round(float(player['xA']), 2),
                'games': player['games']
            }
            return stats
            
    return None

@app.route('/')
def index():
    seasons = ["2020", "2021", "2022", "2023"]
    return render_template('index.html', seasons=seasons)

@app.route('/result', methods=['POST'])
async def result():
    player_name = request.form['player_name']
    season = request.form['season']
    
    stats = await get_player_stats(player_name, season)
    
    return render_template('result.html', player_name=player_name, season=season, stats=stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
