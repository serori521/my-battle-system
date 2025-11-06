# game_actions.py

# --- ユーティリティ関数 ---
def _clamp_int(x):
    return int(max(0, round(x)))

def _damage(attacker, defender, mult=1.0):
    atk = attacker["attack"] * mult
    dmg = _clamp_int(atk - defender["defense"])
    return max(0, dmg)

# --- アクションの設計図（基底クラス） ---
class Action:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost

    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        # 継承先で具体的な処理を記述する
        raise NotImplementedError

# --- 各アクションの定義 ---

class Attack(Action):
    def __init__(self):
        super().__init__("攻撃", 1)

    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        dealt = _damage(attacker, defender, mult=combo_mult)
        defender["HP"] = _clamp_int(defender["HP"] - dealt)
        log_events.append(f"{attacker['name']}の{self.name}: {defender['name']}に{dealt}ダメージ")

class StrongAttack(Action):
    def __init__(self):
        super().__init__("強撃", 2)

    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        mult = 2.2 * combo_mult # コンボ倍率を乗算
        dealt = _damage(attacker, defender, mult=mult)
        defender["HP"] = _clamp_int(defender["HP"] - dealt)
        
        log_message = f"{attacker['name']}の{self.name}"
        if combo_mult > 1.0:
            log_message = f"コンボスキル！ {attacker['name']}の『超・強撃』"

        log_events.append(f"{log_message}: {defender['name']}に{dealt}ダメージ")

class Defend(Action):
    def __init__(self):
        super().__init__("防御", 1)

    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        old_def = attacker["defense"]
        attacker["defense"] = _clamp_int(attacker["defense"] * 1.1 + 1)
        log_events.append(f"{attacker['name']}の防御力上昇: {old_def} → {attacker['defense']}")

class Charge(Action):
    def __init__(self):
        super().__init__("ためる", 1)
    
    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        old_att = attacker["attack"]
        attacker["attack"] = _clamp_int(attacker["attack"] * 1.1 + 2)
        log_events.append(f"{attacker['name']}の攻撃力上昇: {old_att} → {attacker['attack']}")

class Insult(Action):
    def __init__(self):
        super().__init__("侮辱", 1)

    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        old_att = defender["attack"]
        defender["attack"] = _clamp_int(defender["attack"] - (attacker["attack"] / 10))
        log_events.append(f"{attacker['name']}の侮辱で{defender['name']}の攻撃力減少: {old_att} → {defender['attack']}")

class Hide(Action):
    def __init__(self):
        super().__init__("隠れる", 1)

    def execute(self, attacker, defender, log_events, combo_mult=1.0):
        log_events.append(f"{attacker['name']}は隠れている")

# --- アクション管理用の辞書 ---
# アクション名からクラスのインスタンスを引けるようにする
ACTIONS = {
    "攻撃": Attack(),
    "強撃": StrongAttack(),
    "防御": Defend(),
    "ためる": Charge(),
    "侮辱": Insult(),
    "隠れる": Hide(),
}

# コスト表を自動生成
COSTS = {name: action.cost for name, action in ACTIONS.items()}