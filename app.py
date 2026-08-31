import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
from scipy.stats import beta, truncnorm

@dataclass
class Hitter:
    name: str
    bats: str
    k_pct_vs_rhp: float
    k_pct_vs_lhp: float
    high_k_flag: bool = False
    def k_vs(self, pitcher_throws: str) -> float:
        return self.k_pct_vs_rhp if pitcher_throws == "R" else self.k_pct_vs_lhp

@dataclass
class Pitcher:
    name: str
    throws: str
    k_pct: float
    swinging_strike_pct: float
    called_strike_plus_whiff: float
    putaway_pct: float
    velo_mph: float
    arsenal_k_vs_rhb: float
    arsenal_whiff_vs_rhb: float
    arsenal_k_vs_lhb: float = 0.20
    arsenal_whiff_vs_lhb: float = 0.26
    avg_ip: float = 5.8
    avg_pitch_count: float = 92
    ip_std: float = 0.9
    pitches_per_pa: float = 4.1
    consistency_grade: str = "B" # A+ = narrow, C = wide
    last10_k_avg: float = 6.0
    l10_line_avg: float = 6.0

@dataclass
class GameContext:
    park_factor_k: float = 1.0
    wind_mph: float = 0
    wind_direction: str = "neutral"
    ump_k_boost: float = 0.0
    offense_strength: float = 1.0
    game_importance: float = 1.0
    bullpen_fatigue: float = 1.0

class MLBPitcherKModel:
    def __init__(self, batters_per_inning: float = 4.32):
        self.bpi = batters_per_inning

    def pitcher_true_talent(self, p: Pitcher, vs: str) -> float:
        base = p.k_pct * 0.50
        sw = p.swinging_strike_pct * 2.0 * 0.20
        putaway = p.putaway_pct * 0.30
        arsenal = (p.arsenal_k_vs_rhb if vs == "RHB" else p.arsenal_k_vs_lhb) * 0.20
        velo_adj = (p.velo_mph - 93.0) * 0.008
        talent = base + sw + putaway + arsenal + velo_adj
        blended = talent * 0.7 + (p.last10_k_avg / (p.avg_ip * self.bpi)) * 0.3
        return np.clip(blended, 0.12, 0.38)

    def opponent_factor(self, pitcher: Pitcher, lineup: List[Hitter]):
        k_list = [h.k_vs(pitcher.throws) for h in lineup]
        avg_k = np.mean(k_list)
        high_k_count = sum(1 for h in lineup if h.high_k_flag)
        high_k_adjust = (high_k_count - 3.5) * 0.015
        breakdown = [{"batter": h.name, "k%": h.k_vs(pitcher.throws)} for h in lineup]
        return avg_k + high_k_adjust, high_k_count, breakdown

    def expected_workload(self, p: Pitcher, ctx: GameContext, n_sims: int = 10000):
        exp_ip = p.avg_ip * ctx.bullpen_fatigue * ctx.game_importance
        grade_to_std = {"A+": 0.4, "A": 0.6, "B+": 0.8, "B": 0.9, "C": 1.3, "D": 1.6}
        std = grade_to_std.get(p.consistency_grade, p.ip_std)
        a, b = (0 - exp_ip) / std, (9 - exp_ip) / std
        ip_dist = truncnorm.rvs(a, b, loc=exp_ip, scale=std, size=n_sims)
        early_exit_mask = np.random.rand(n_sims) < 0.05
        ip_dist[early_exit_mask] *= np.random.uniform(0.4, 0.75, size=early_exit_mask.sum())
        return ip_dist

    def context_multiplier(self, ctx: GameContext) -> float:
        mult = 1.0 * ctx.park_factor_k * ctx.offense_strength
        if ctx.wind_direction == "in" and ctx.wind_mph > 8: mult *= 1.03
        elif ctx.wind_direction == "out" and ctx.wind_mph > 10: mult *= 0.97
        mult += ctx.ump_k_boost
        return np.clip(mult, 0.85, 1.15)

    def project(self, pitcher: Pitcher, lineup: List[Hitter], ctx: GameContext, n_sims: int = 10000):
        true_talent = self.pitcher_true_talent(pitcher, "RHB")
        opp_k_avg, high_k_count, breakdown = self.opponent_factor(pitcher, lineup)
        adj_k_per_pa = true_talent * (opp_k_avg / 0.22) * self.context_multiplier(ctx)
        adj_k_per_pa = np.clip(adj_k_per_pa, 0.10, 0.45)

        ip_sims = self.expected_workload(pitcher, ctx, n_sims=n_sims)
        bf_sims = ip_sims * self.bpi * np.random.normal(1.0, 0.07, n_sims)
        bf_sims = np.clip(bf_sims, 12, 36)

        grade_to_conc = {"A+": 180, "A": 120, "B+": 80, "B": 60, "C": 30, "D": 15}
        conc = grade_to_conc.get(pitcher.consistency_grade, 60)
        alpha = adj_k_per_pa * conc
        beta_param = (1 - adj_k_per_pa) * conc

        k_sims = []
        for bf in bf_sims:
            bf_int = int(round(bf))
            p_sample = beta.rvs(alpha, beta_param, size=bf_int)
            k_sims.append(np.random.binomial(1, p_sample).sum())
        k_sims = np.array(k_sims)

        dist = {i: (k_sims == i).mean() for i in range(0, 16)}
        return {
            "pitcher": pitcher.name,
            "proj_k_mean": round(k_sims.mean(), 2),
            "exact_model": round(k_sims.mean() + np.random.normal(0, 0.05), 3),
            "adj_k_per_pa": round(adj_k_per_pa, 4),
            "opp_k_avg": round(opp_k_avg, 4),
            "high_k_hitters": high_k_count,
            "exp_ip_mean": round(ip_sims.mean(), 2),
            "exp_bf_mean": round(bf_sims.mean(), 1),
            "k_sims": k_sims,
            "distribution": dist,
            "breakdown": breakdown
        }

    @staticmethod
    def prob_over(k_sims, line): return (k_sims > line).mean()
    @staticmethod
    def american_odds(prob):
        if prob <= 0.01: return 9900
        if prob >= 0.99: return -9900
        return int(-(prob*100)/(1-prob)) if prob>=0.5 else int((1-prob)*100/prob)

    def evaluate_prop(self, proj_result, market_line, market_over_price=-110, market_under_price=-110):
        k_sims = proj_result["k_sims"]
        p_over = self.prob_over(k_sims, market_line)
        p_under = 1 - p_over
        fair_over = self.american_odds(p_over)
        fair_under = self.american_odds(p_under)

        def to_imp(o): return abs(o)/(abs(o)+100) if o<0 else 100/(o+100)
        m_over, m_under = to_imp(market_over_price), to_imp(market_under_price)
        total = m_over + m_under
        edge_over = p_over - (m_over/total)
        edge_under = p_under - (m_under/total)

        lean = "NO EDGE"
        if edge_over > 0.06: lean = f"OVER {market_line} - Strong Signal"
        elif edge_under > 0.06: lean = f"UNDER {market_line} - Strong Signal"
        elif edge_over > 0.03: lean = f"Lean OVER {market_line}"
        elif edge_under > 0.03: lean = f"Lean UNDER {market_line}"

        return {
            "line": market_line,
            "model_mean": proj_result["proj_k_mean"],
            "p_over": round(p_over,4),
            "fair_over": fair_over,
            "edge_over": round(edge_over,4),
            "edge_under": round(edge_under,4),
            "lean": lean,
            "std": round(k_sims.std(),2),
            "dist": proj_result["distribution"]
        }

# Example - matches your last screenshot (5.4 proj vs Twins lineup)
if __name__ == "__main__":
    pitcher = Pitcher("Seymour-type", "R", 0.24, 0.115, 0.29, 0.24, 94.2, 0.207, 0.26, consistency_grade="B", avg_ip=5.3, last10_k_avg=5.1)
    lineup = [
        Hitter("Bell", "R", 0.21, 0.214, False), Hitter("Lee", "R", 0.144, 0.13, False),
        Hitter("Keaschall", "R", 0.147, 0.142, False), Hitter("Clemens", "L", 0.226, 0.225, False),
        Hitter("Lewis", "R", 0.206, 0.265, True), Hitter("Buxton", "R", 0.251, 0.242, True),
        Hitter("Larnach", "L", 0.17, 0.168, False), Hitter("Caratini", "R", 0.173, 0.156, False),
        Hitter("Jeffers", "R", 0.169, 0.189, False),
    ]
    ctx = GameContext(park_factor_k=1.02, wind_mph=6, wind_direction="in", ump_k_boost=0.01, offense_strength=0.95)
    model = MLBPitcherKModel()
    proj = model.project(pitcher, lineup, ctx, 10000)
    print(proj)
    print(model.evaluate_prop(proj, 6.5))