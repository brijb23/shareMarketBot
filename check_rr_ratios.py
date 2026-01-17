import json

data = json.load(open('NIFTY50_RECOMMENDATION_20260110_150713.json'))

print('Stock            | Entry    | Target1  | Stop     | Risk%  | Reward% | R:R')
print('-' * 75)

for d in data[:15]:
    entry = d['entry_price']
    target1 = d['target_1']
    stop = d['stop_loss']
    risk_pct = abs((entry - stop) / entry * 100)
    reward_pct = ((target1 - entry) / entry * 100)
    rr_calc = reward_pct / risk_pct if risk_pct > 0 else 0
    rr_stored = d['risk_metrics']['reward_to_risk_ratio']
    
    print(f'{d["symbol"]:15s} | {entry:8.2f} | {target1:8.2f} | {stop:8.2f} | {risk_pct:6.2f}% | {reward_pct:6.2f}% | {rr_calc:5.2f}:1')
