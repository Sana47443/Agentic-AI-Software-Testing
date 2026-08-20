from __future__ import annotations
from .models import RiskScore, ScheduleDecision

class TestScheduler:
    def decide(self, changed_modules:list[str], risk_scores:list[RiskScore], threshold:float=0.65)->ScheduleDecision:
        risk={x.module:x.risk_score for x in risk_scores}
        high=[m for m in changed_modules if risk.get(m,0.0)>=threshold]
        if high:
            reason=f"Regression recommended because changed module(s) exceed the risk threshold: {', '.join(high)}."
        else:
            reason="No changed module exceeds the configured risk threshold; a scheduled or targeted run may still be appropriate."
        return ScheduleDecision(should_run_regression=bool(high),reason=reason,changed_modules=changed_modules,high_risk_changed_modules=high,threshold=threshold)
