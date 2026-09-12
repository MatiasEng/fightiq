from api.predict import predict 
r = predict("Islam Makhachev", "Ilia Topuria")
print(f"Win prob: {r['fighter_a_win_prob']} vs {r['fighter_b_win_prob']}")
print(f"Winner: {r['predicted_winner']}\n")
for e in r["explanation"]:
    print(f"  {e['feature']:<22} {e['shap_value']:+7.4f}  ({e['direction']})")