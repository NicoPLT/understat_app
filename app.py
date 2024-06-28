from flask import Flask, render_template, request, jsonify
import aiohttp
import asyncio
import json
import logging
from understat import Understat

app = Flask(__name__)

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player_names')
async def player_names():
    try:
        season = request.args.get('season')
        if not season:
            return jsonify({'error': 'Missing season parameter'}), 400

        async with aiohttp.ClientSession() as session:
            understat = Understat(session)
            players = await understat.get_league_players("epl", season)

        player_names = [player['player_name'] for player in players]
        return jsonify(player_names)
    except Exception as e:
        logging.error(f"Error in /player_names: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/player_stats', methods=['POST'])
async def player_stats():
    try:
        data = await request.get_json()
        player_name = data.get('player_name')
        season = data.get('season')

        if not player_name or not season:
            return jsonify({'error': 'Missing player_name or season parameter'}), 400

        async with aiohttp.ClientSession() as session:
            understat = Understat(session)
            players = await understat.get_league_players("epl", season)

            for player in players:
                if player['player_name'] == player_name:
                    return jsonify({
                        'player_name': player['player_name'],
                        'goals': player['goals'],
                        'assists': player['assists'],
                        'xG': round(player['xG'], 2),
                        'xA': round(player['xA'], 2),
                    })
        return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        logging.error(f"Error in /player_stats: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run()

