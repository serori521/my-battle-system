# game_logic.py

import numpy as np
from copy import deepcopy

from config import game_config, PLAYER_INITIAL, ENEMY_INITIAL, block_max
from game_actions import ACTIONS, COSTS

# --- グローバルなゲーム状態 ---
game_state = {}

# --- ロジック関数 ---

def reset_game_logic():
    """ゲームの状態を完全に初期化する"""
    global game_state
    game_state.update({
        "player": deepcopy(PLAYER_INITIAL),
        "enemy": deepcopy(ENEMY_INITIAL),
        "player_actions": [],
        "battle_logs": [],
        "turn_number": 1,
        "all_turn_logs": [],
        "game_over": False,
        "winner": None,
        "current_log_index": 0,
        "showing_logs": False,
        "enemy_action_preview": [] # 敵の行動予告用
    })

def total_cost(turn):
    """アクションリストの合計コストを計算"""
    return sum(COSTS[a[1]] for a in turn)

def add_action_logic(action_name):
    """プレイヤーのアクションを追加する"""
    if action_name not in COSTS:
        return False, "未知の行動です"
    
    now = total_cost(game_state["player_actions"])
    nxt = now + COSTS[action_name]

    if nxt <= block_max:
        game_state["player_actions"].append((nxt, action_name))
        return True, "アクションを追加しました"
    else:
        return False, f"コスト不足で{action_name}を追加できません"

def make_enemy_action_logic():
    """敵の行動を生成し、予告も作成する"""
    turn = []
    action_keys = list(COSTS.keys())
    while True:
        remain = block_max - total_cost(turn)
        candidates = [a for a in action_keys if COSTS[a] <= remain]
        if not candidates:
            break
        pick = np.random.choice(candidates)
        now = total_cost(turn)
        nxt = now + COSTS[pick]
        turn.append((nxt, pick))
    
    preview = []
    if game_config["use_enemy_preview"]:
        # 予告を生成（今回は単純に行動名のリストを作成）
        preview = sorted([action[1] for action in turn])

    return turn, preview

def check_for_combos(player_actions):
    """コマンドスキル（コンボ）が成立しているかチェック"""
    combo_effects = {} # {index: effect}
    action_names = [a[1] for a in sorted(player_actions)] # タイムライン順にソート

    # 例：「ためる」→「強撃」のコンボ
    for i in range(len(action_names) - 1):
        if action_names[i] == "ためる" and action_names[i+1] == "強撃":
            # 強撃のアクションが何番目のindexかを探す
            target_index = sorted(player_actions)[i+1][0]
            # 効果を辞書に保存（今回は倍率1.5倍）
            combo_effects[target_index] = {"mult": 1.5}
            # 一度コンボに使ったアクションは消費される（連続コンボを防ぐ）
            action_names[i] = None
            action_names[i+1] = None
    
    return combo_effects

def action_logic(player, enemy, player_actions, enemy_actions):
    """戦闘シミュレーションを実行する"""
    logs = []
    
    # コンボチェック
    combo_effects = {}
    if game_config["use_combo_system"]:
        combo_effects = check_for_combos(player_actions)

    for index in range(1, block_max + 1):
        p_act_tuple = next((a for a in player_actions if a[0] == index), None)
        e_act_tuple = next((a for a in enemy_actions if a[0] == index), None)

        p_name = p_act_tuple[1] if p_act_tuple else None
        e_name = e_act_tuple[1] if e_act_tuple else None

        if not p_name and not e_name:
            continue

        log_entry = {"index": index, "player_action": p_name, "enemy_action": e_name, "events": []}

        p_hide = (p_name == "隠れる")
        e_hide = (e_name == "隠れる")
        
        # --- プレイヤーのアクション実行 ---
        if p_name and not e_hide:
            action_obj = ACTIONS.get(p_name)
            if action_obj:
                combo_mult = combo_effects.get(index, {}).get("mult", 1.0)
                action_obj.execute(attacker=player, defender=enemy, log_events=log_entry["events"], combo_mult=combo_mult)
        elif p_name and e_hide:
            log_entry["events"].append("敵が隠れていたためプレイヤーの行動は無効")

        # --- 敵のアクション実行 ---
        if e_name and not p_hide:
            action_obj = ACTIONS.get(e_name)
            if action_obj:
                action_obj.execute(attacker=enemy, defender=player, log_events=log_entry["events"])
        elif e_name and p_hide:
            log_entry["events"].append("プレイヤーが隠れていたため敵の行動は無効")

        log_entry["player_stats"] = dict(player)
        log_entry["enemy_stats"] = dict(enemy)
        logs.append(log_entry)

        if player["HP"] <= 0 or enemy["HP"] <= 0:
            break
            
    return logs


def start_battle_logic():
    """バトル開始の全体的な処理"""
    if game_state["game_over"]:
        return {"success": False, "error": "ゲーム終了済みです。"}
    if not game_state["player_actions"]:
        return {"success": False, "error": "アクションが設定されていません"}

    enemy_actions, enemy_preview = make_enemy_action_logic()
    player_copy = deepcopy(game_state["player"])
    enemy_copy = deepcopy(game_state["enemy"])

    logs = action_logic(player_copy, enemy_copy, game_state["player_actions"], enemy_actions)

    # ターンログを保存
    turn_log = {
        "turn": game_state["turn_number"],
        "player_actions": game_state["player_actions"].copy(),
        "enemy_actions": enemy_actions.copy(),
        "logs": logs.copy(),
    }
    game_state["all_turn_logs"].append(turn_log)

    game_state["player"] = player_copy
    game_state["enemy"] = enemy_copy
    game_state["battle_logs"] = logs

    result = "continue"
    if game_state["player"]["HP"] <= 0:
        result = "player_lose"
        game_state["game_over"] = True
        game_state["winner"] = "enemy"
    elif game_state["enemy"]["HP"] <= 0:
        result = "player_win"
        game_state["game_over"] = True
        game_state["winner"] = "player"

    game_state["current_log_index"] = 0
    game_state["showing_logs"] = True

    return {
        "success": True, "logs": logs, "result": result,
        "enemy_actions": enemy_actions, "enemy_action_preview": enemy_preview
    }

# 初期化を最初に呼び出しておく
reset_game_logic()