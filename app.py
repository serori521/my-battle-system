# app.py

from flask import Flask, render_template, request, jsonify
import os

# configとlogicの関数をインポート
import config
import game_logic
from game_actions import COSTS

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game_state')
def get_game_state():
    # game_stateとcosts, configを返す
    return jsonify({
        "gameState": game_logic.game_state,
        "costs": COSTS,
        "blockMax": config.block_max,
        "gameConfig": config.game_config
    })

@app.route('/api/update_config', methods=['POST'])
def update_config():
    """機能のON/OFF設定を更新するAPI"""
    new_config = request.json
    if 'use_combo_system' in new_config:
        config.game_config['use_combo_system'] = bool(new_config['use_combo_system'])
    if 'use_enemy_preview' in new_config:
        config.game_config['use_enemy_preview'] = bool(new_config['use_enemy_preview'])
    return jsonify({"success": True, "gameConfig": config.game_config})

@app.route('/api/add_action', methods=['POST'])
def add_player_action():
    action_name = request.json.get('action')
    success, message = game_logic.add_action_logic(action_name)
    if success:
        return jsonify({"success": True, "player_actions": game_logic.game_state["player_actions"]})
    else:
        return jsonify({"success": False, "error": message})

@app.route('/api/reset_actions', methods=['POST'])
def reset_actions():
    game_logic.game_state["player_actions"] = []
    return jsonify({"success": True})

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    game_logic.reset_game_logic()
    return jsonify({"success": True})

@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    response = game_logic.start_battle_logic()
    return jsonify(response)

@app.route('/api/next_turn', methods=['POST'])
def next_turn():
    """ログ表示後、次のターンに進める"""
    if not game_logic.game_state["game_over"]:
        game_logic.game_state["turn_number"] += 1
        game_logic.game_state["player_actions"] = []
        game_logic.game_state["battle_logs"] = []
        game_logic.game_state["showing_logs"] = False
        game_logic.game_state["enemy_action_preview"] = [] # 予告をリセット
    return jsonify({"success": True})


if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # index.htmlがなければ簡単なものを作成
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html><html><head><title>Game</title></head><body><h1>Game Loading...</h1><p>JavaScriptを有効にしてください。</p></body></html>")
            
    app.run(debug=True, host='0.0.0.0', port=8080)