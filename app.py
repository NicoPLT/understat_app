from flask import Flask, request, jsonify, render_template
import aiohttp
import asyncio
from understat import Understat

app = Flask(__name__)

@app.route('/')
def index():
    seasons = ['2019', '2020', '2021', '2022', '2023']  # Aggiunta della stagione 2023
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
        players = await understat.get_league_players("serie_a", season)  # Cambia "epl" a "serie_a"
        player_names = [player['player_name'] for player in players]
        return player_names

@app.route('/result', methods=['POST'])
def result():
    player_name = request.form['player_name']
    season = request.form['season']
    
    # Puoi aggiungere logica per ottenere e visualizzare le statistiche del giocatore
    # Per ora, passiamo semplicemente i dati al template di risultato
    return render_template('result.html', player_name=player_name, season=season)

if __name__ == '__main__':
    app.run(debug=True)


