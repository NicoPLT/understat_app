from flask import Flask, render_template, request, jsonify
import understat
import aiohttp
import asyncio
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_player_stats(player_name, season):
    leagues = ["Serie_A", "Ligue_1", "Bundesliga", "EPL", "La_Liga"]
    async with aiohttp.ClientSession() as session:
        understat_instance = understat.Understat(session)
        player_data = []

        for league in leagues:
            players = await understat_instance.get_league_players(league, season.split('/')[0])
            logging.info(f"Fetched {len(players)} players for {league} in season {season}")
            for player in players:
                if player['player_name'] == player_name:
                    player['league'] = league
                    player_data.append(player)

        if not player_data:
            logging.warning(f"No player data found for {player_name} in season {season}")
            return None

        player_data.sort(key=lambda x: int(x.get('games', 0)), reverse=True)
        player = player_data[0]
        logging.info(f"Selected player data: {json.dumps(player, indent=2)}")

        xG = float(player.get('xG', 0))
        xA = float(player.get('xA', 0))
        minutes = int(player.get('time', 0))
        key_passes = int(player.get('key_passes', 0))
        goals = int(player.get('goals', 0))
        assists = int(player.get('assists', 0))
        shots = int(player.get('shots', 0))
        is_goalkeeper = player.get('position', '') == 'GK'
        
        player_id = player['id']

        clean_sheets = 0
        games_played = int(player.get('games', 0))
        if is_goalkeeper:
            try:
                player_matches = await understat_instance.get_player_matches(player_id)
                logging.info(f"Total matches fetched for player {player_name}: {len(player_matches)}")
                
                current_season_matches = [match for match in player_matches if match['season'] == season.split('/')[0]]
                logging.info(f"Matches in current season {season}: {len(current_season_matches)}")
                
                for match in current_season_matches:
                    logging.debug(f"Processing match: {json.dumps(match, indent=2)}")

                    player_minutes = int(match.get('time', 0))
                    h_goals = int(match.get('h_goals', 0))
                    a_goals = int(match.get('a_goals', 0))
                    player_team = match.get('h_team') if match.get('h_team') != match.get('a_team') else match.get('a_team')
                    goals_conceded = a_goals if player_team == match.get('h_team') else h_goals
                    is_starter = match.get('position', '') != 'Sub'

                    logging.info(f"Match details - Date: {match.get('date')}, Minutes: {player_minutes}, Goals conceded: {goals_conceded}, Team: {player_team}, Starter: {is_starter}")

                    if is_starter and player_minutes >= 25 and goals_conceded == 0:
                        clean_sheets += 1
                        logging.info(f"Clean sheet recorded. Total: {clean_sheets}")

            except Exception as e:
                logging.error(f"Error processing goalkeeper data: {str(e)}")

        logging.info(f"Final stats for {player_name} - Clean sheets: {clean_sheets}, Games played: {games_played}")

        xG90 = round(xG / (minutes / 90), 2) if minutes > 0 else 0
        xA90 = round(xA / (minutes / 90), 2) if minutes > 0 else 0

        heatmap_url = f"https://understat.com/player/{player_id}"

        return {
            'xG': round(xG, 2),
            'xA': round(xA, 2),
            'games': games_played,
            'minutes': minutes,
            'xG90': xG90,
            'xA90': xA90,
            'key_passes': key_passes,
            'goals': goals,
            'assists': assists,
            'shots': shots,
            'clean_sheets': clean_sheets,
            'heatmap_url': heatmap_url,
            'league': player['league'],
            'is_goalkeeper': is_goalkeeper
        }

@app.route('/')
def index():
    seasons = ["2024/2025", "2023/2024", "2022/2023", "2021/2022", "2020/2021", "2019/2020"]
    return render_template('index.html', seasons=seasons, default_season="2024/2025")

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
            players = await understat_instance.get_league_players(league, season.split('/')[0])
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

@app.route('/credits.html')
def credits():
    return render_template('credits.html')

if __name__ == '__main__':
    app.run(debug=True)