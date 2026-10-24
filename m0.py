"""D1/M0 finite-horizon age--deadline resolution control.

Mathematical contract: an action is taken at the beginning of a unit interval.
Success within the final interval meets the deadline. Conditional on no success,
(a, ell) -> (a+1, ell-1). There is one continuing nonterminal state per step.
This prototype represents single-stage resolution, not a full logistics journey.

Costs: c*u plus failure penalty K. In the activation-charge relaxation,
active cost is (c + lambda)*u. In the *distinct* unresolved-only passive-subsidy
model, passive action receives -s each unresolved interval. These models are
NOT asserted to have equivalent indices.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import exp, isfinite
from typing import Callable
import random

Hazard = Callable[[int], float]

@dataclass(frozen=True)
class M0:
    p0: Hazard
    p1: Hazard
    c: float = 8.0
    K: float = 100.0

    def __post_init__(self):
        if not (isfinite(self.c) and isfinite(self.K) and self.c >= 0 and self.K >= 0):
            raise ValueError('Nonnegative finite cost c and terminal penalty K required.')

    def probability(self, u: int, a: int) -> float:
        if u not in (0, 1) or a < 0 or not isinstance(a, int):
            raise ValueError('Expected u in {0,1} and a nonnegative integer dwell age.')
        p = self.p1(a) if u else self.p0(a)
        if not isfinite(p) or not (0 <= p <= 1):
            raise ValueError(f'Invalid probability p_{u}({a})={p}.')
        return float(p)

    def solve(self, age: int, slack: int, *, charge: float = 0.0,
              passive_subsidy: float = 0.0) -> tuple[float, int]:
        """Return (cost-to-go, optimal initial action) with passive tie-breaking.

        Exactly one of charge and passive_subsidy may be nonzero. Neither
        parameter represents a proven Whittle index.
        """
        if (not isinstance(age, int) or not isinstance(slack, int)
            or age < 0 or slack < 0):
            raise ValueError('age and slack must be nonnegative integers')
        if charge != 0.0 and passive_subsidy != 0.0:
            raise ValueError('Charge and passive subsidy are different relaxations.')
        if not (isfinite(charge) and isfinite(passive_subsidy)):
            raise ValueError('Relaxation parameters must be finite.')
        @lru_cache(None)
        def dp(a: int, l: int):
            if l == 0:
                return self.K, 0
            cont = dp(a + 1, l - 1)[0]
            q0 = -passive_subsidy + (1.0 - self.probability(0, a)) * cont
            q1 = self.c + charge + (1.0 - self.probability(1, a)) * cont
            return (q0, 0) if q0 <= q1 else (q1, 1)
        return dp(age, slack)

    def evaluate_sequence(self, age: int, slack: int, actions: tuple[int, ...],
                          *, charge: float = 0.0, passive_subsidy: float = 0.0) -> float:
        """Exact cost of a time-dependent policy along the unresolved path."""
        if len(actions) != slack or any(a not in (0,1) for a in actions):
            raise ValueError('One binary action for each possible unresolved interval.')
        cost, surv = 0.0, 1.0
        for t, u in enumerate(actions):
            cost += surv * (self.c * u + charge * u - passive_subsidy * (1 - u))
            surv *= 1.0 - self.probability(u, age + t)
        return cost + surv * self.K

    def exhaustive(self, age: int, slack: int, **kwargs) -> float:
        if slack > 18:
            raise ValueError('Exhaustive enumeration reserved for short horizons.')
        return min(self.evaluate_sequence(age, slack, acts, **kwargs)
                   for acts in product((0,1), repeat=slack))

    def simulate(self, age: int, slack: int, *, n: int, seed: int) -> tuple[float,float,float]:
        """Empirical cost, standard error, failure frequency under base optimal policy."""
        if n < 2:
            raise ValueError('At least two replications are required.')
        rng = random.Random(seed)
        memo = {}
        def action(a, l):
            if (a,l) not in memo:
                memo[a,l] = self.solve(a,l)[1]
            return memo[a,l]
        costs, failures = [], 0
        for _ in range(n):
            cost = 0.0
            for t in range(slack):
                u = action(age+t,slack-t)
                cost += self.c*u
                if rng.random() < self.probability(u,age+t):
                    break
            else:
                cost += self.K
                failures += 1
            costs.append(cost)
        mean = sum(costs)/n
        var = sum((x-mean)**2 for x in costs)/(n-1)
        return mean, (var/n)**0.5, failures/n


def illustrative_model() -> M0:
    """Synthetic age-dependent probabilities satisfying a sufficient age ordering."""
    def p0(a): return 0.32 * exp(-0.075*a)
    def p1(a):
        q = p0(a)
        return q + (1.0-q)*0.35
    return M0(p0,p1,c=8.0,K=100.0)


def test_ordering(model: M0, *, ages: range, slacks: range) -> dict:
    """Numerical theorem diagnostic, NOT a replacement for analytical proof."""
    errors = []
    for l in slacks:
        for a in ages:
            if model.solve(a+1,l)[0] + 1.e-11 < model.solve(a,l)[0]:
                errors.append(('age-value',a,l))
            if l >= 1 and model.solve(a,l)[0] > model.solve(a,l-1)[0]+1.e-11:
                errors.append(('slack-value',a,l))
            if l >= 1:
                delta = model.probability(1,a)-model.probability(0,a)
                advantage = delta*model.solve(a+1,l-1)[0]-model.c
                if (model.solve(a,l)[1] == 1) != (advantage > 1.e-12):
                    errors.append(('decision-identity',a,l))
    return {'states_checked':len(ages)*len(slacks),'errors':errors}


def charge_passive_set_reversals(model: M0, *, ages: range, slacks: range,
                                 charges: list[float]) -> list:
    """Check observed passive-set nesting as activation charge increases.

    Absence of a reversal on a finite grid DOES NOT prove indexability.
    """
    if charges != sorted(charges):
        raise ValueError('Charges must be in increasing order.')
    reversals=[]
    for a in ages:
        for l in slacks:
            acts=[model.solve(a,l,charge=x)[1] for x in charges]
            for j in range(1,len(acts)):
                if acts[j] > acts[j-1]:
                    reversals.append((a,l,charges[j-1],charges[j]))
    return reversals
