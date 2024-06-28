from flask import Flask, request, jsonify, render_template
import aiohttp
import asyncio
from understat import Understat
import logging

app = Flask(__name__)

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    seasons = ['2019', '2020', '2021', '2022', '2023']
    return render_template('index.html', seasons=seasons)

@app.route('/player_names', methods=['GET'])
def get_player_names():
    season = request.args.get('season')
    if not season:
        return jsonify([]), 400
    
    try:
        player_names = asyncio.run(fetch_player_names(season))
        return jsonify(player_names)
    except Exception as e:
        logging.error("Errore nel caricamento dei nomi dei giocatori", exc_info=True)
        return jsonify({"error": "Errore nel caricamento dei nomi dei giocatori"}), 500

async def fetch_player_names(season):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        players = await understat.get_league_players("serie_a", season)
        player_names = [player['player_name'] for player in players]
        return player_names

@app.route('/result', methods=['POST'])
def result():
    player_name = request.form.get('player_name')
    season = request.form.get('season')
    
    if not player_name or not season:
        logging.error("player_name o season non forniti.")
        return render_template('error.html', message="player_name o season non forniti."), 400
    
    try:
        logging.info(f"Caricamento dei risultati per {player_name} nella stagione {season}")
        stats = asyncio.run(fetch_player_stats(player_name, season))
        return render_template('result.html', player_name=player_name, stats=stats)
    except Exception as e:
        logging.error("Errore nella visualizzazione dei risultati", exc_info=True)
        return render_template('error.html', message="Errore nella visualizzazione dei risultati"), 500

async def fetch_player_stats(player_name, season):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        players = await understat.get_league_players("serie_a", season)
        player_stats = next((player for player in players if player['player_name'] == player_name), None)
        if player_stats is None:
            raise ValueError(f"Player {player_name} not found in season {season}")
        return player_stats

if __name__ == '__main__':
    app.run(debug=True)
