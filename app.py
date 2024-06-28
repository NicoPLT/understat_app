from flask import Flask, request, jsonify, render_template
import requests
from understat import Understat
import aiohttp
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    seasons = ['2019', '2020', '2021', '2022']  # Esempio di stagioni, puoi caricarle dinamicamente se necessario
    return render_template('index.html', seasons=seasons)

@app.route('/player_names', methods=['GET'])
def get_player_names():
    season = request.args.get('season')
    if not season:
        return jsonify([]), 400  # Ritorna una lista vuota se la stagione non è specificata
    
    # Fetch player names from Understat
    player_names = asyncio.run(fetch_player_names(season))
    return jsonify(player_names)

async def fetch_player_names(season):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        players = await understat.get_league_players("epl", season)
        player_names = [player['player_name'] for player in players]
        return player_names

if __name__ == '__main__':
    app.run(debug=True)

