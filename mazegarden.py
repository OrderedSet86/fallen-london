# Best trade in at 1-100 CP
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class Reward:
    echoes: int
    trades: dict = field(default_factory=Counter)


@dataclass
class Trade:
    item: str
    cost: int
    echoes: float


trades = [
    Trade('Silk Scrap', 1, 0.5),
    Trade('Surface-Silk Scrap', 6, 6),
    Trade('Whisper-Satin Scrap', 15, 15),
    Trade('Correspondence Plaque', 28, 28),
    Trade('Thirsty-Bombazine Scrap/Glass Gazette', 66, 65),
]

best_reward = [Reward(0, Counter())]
for i in range(1, 101):
    possible_trades = [x for x in trades if x.cost <= i]
    expected_value_arr = []
    for trade in possible_trades:
        trade_value = trade.echoes
        next_reward_offset = i - trade.cost
        expected_value = trade_value + best_reward[next_reward_offset].echoes
        expected_value_arr.append((expected_value, trade, next_reward_offset))

    best_value, best_trade, best_offset = sorted(expected_value_arr, key=lambda x: x[0], reverse=True)[0]
    own_trades = deepcopy(best_reward[best_offset].trades)
    own_trades[best_trade.item] += 1
    best_reward.append(
        Reward(best_value, own_trades)
    )


for i, rw in enumerate(best_reward):
    best_gain = i
    loss = best_gain - rw.echoes
    print(f'{i}: {loss} {dict(rw.trades)}')