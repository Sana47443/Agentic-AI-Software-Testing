from __future__ import annotations
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from .models import RiskScore
FEATURES=["loc","churn","complexity","prior_bugs"]
TARGET="future_defects"

class DefectPredictor:
    def __init__(self, random_state:int=42):
        self.model=RandomForestRegressor(n_estimators=200, random_state=random_state)
    def train_and_score(self, csv_path:str|Path)->list[RiskScore]:
        df=pd.read_csv(csv_path)
        missing=set(FEATURES+[TARGET,"module"])-set(df.columns)
        if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
        self.model.fit(df[FEATURES],df[TARGET])
        pred=self.model.predict(df[FEATURES])
        lo,hi=float(np.min(pred)),float(np.max(pred))
        risk=np.full_like(pred,0.5,dtype=float) if hi==lo else (pred-lo)/(hi-lo)
        return [RiskScore(module=row["module"],predicted_defects=round(float(p),3),risk_score=round(float(r),3)) for (_,row),p,r in zip(df.iterrows(),pred,risk)]
    def save_model(self,path:str|Path):
        Path(path).parent.mkdir(parents=True,exist_ok=True); joblib.dump(self.model,path)
