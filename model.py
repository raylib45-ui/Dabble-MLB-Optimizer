import pandas as pd

def calculate_ev(line, projection, odds_multiplier):
    diff = projection - line
    prob_over = max(0.1, min(0.9, 0.5 + (diff * 0.1)))
    prob_under = 1 - prob_over
    ev_over = (prob_over * odds_multiplier) - 1
    return {
        "prob_over": round(prob_over, 3), 
        "prob_under": round(prob_under, 3),
        "ev_over": round(ev_over, 3)
    }

if __name__ == "__main__":
    result = calculate_ev(line=7.5, projection=6.8, odds_multiplier=1.1)
    print("Analysis Result:", result)
