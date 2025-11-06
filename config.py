# config.py

# --- ゲームの拡張機能設定 ---
# この値をTrue/Falseすることで、UIから機能をON/OFFできる
game_config = {
    "use_combo_system": True,  # コマンドスキル（コンボ）機能を使うか
    "use_enemy_preview": True, # 敵の行動予告機能を使うか
    "use_missions": False,      # （将来の拡張用）ミッション機能を使うか
}

# --- 基本設定 ---
block_max = 10

# --- キャラクター初期ステータス ---
PLAYER_INITIAL = {
    "HP": 150,
    "attack": 17,
    "defense": 10,
    "name": "プレイヤー" # ログ表示用に名前を追加
}

ENEMY_INITIAL = {
    "HP": 150,
    "attack": 20,
    "defense": 10,
    "name": "敵" # ログ表示用に名前を追加
}