import os
import joblib
import numpy as np
import pandas as pd

CATEGORY_ABBREVIATION_MAP = {
    "A": "Analysis", "B": "Backdoors", "D": "DoS", "E": "Exploits",
    "F": "Fuzzers", "G": "Generic", "R": "Reconnaissance",
    "S": "Shellcode", "W": "Worms", "N": "Normal",
}

SEVERITY_WEIGHTS = {
    "Worms": 5, "Shellcode": 5, "Backdoors": 5, "Backdoor": 5,
    "Exploits": 4, "DoS": 4, "Generic": 3, "Reconnaissance": 2,
    "Analysis": 2, "Fuzzers": 1, "Normal": 0,
}

class MLModelHandler:
    def __init__(self):
        self.models_dir = "models"
        self.preprocessor = None
        self.stage1_model = None
        self.stage2_model = None
        self.cat_encoder = None

    def load_models(self):
        print("Loading ML models and preprocessor...")
        try:
            self.preprocessor = joblib.load(f"{self.models_dir}/preprocessing_pipeline.joblib")
            self.stage1_model = joblib.load(f"{self.models_dir}/stage1_random_forest_smote.joblib")
            self.stage2_model = joblib.load(f"{self.models_dir}/stage2_xgboost_tuned.joblib")
            self.cat_encoder = joblib.load(f"{self.models_dir}/stage2_label_encoder.joblib")
            print("All models loaded successfully!")
        except Exception as e:
            print(f"Error loading model artifacts: {e}")

    def assign_priority_tier(self, risk_score, max_severity=5):
        if risk_score == 0: return "None"
        if risk_score >= 0.70 * max_severity: return "Critical"
        if risk_score >= 0.40 * max_severity: return "High"
        if risk_score >= 0.15 * max_severity: return "Medium"
        return "Low"

    def predict(self, event_data: dict):
        meta_data = {
            "timestamp": event_data.get("timestamp"),
            "srcip": event_data.get("srcip", "Unknown"),
            "dstip": event_data.get("dstip", "Unknown")
        }

        df_raw = pd.DataFrame([event_data])

        try:
            if hasattr(self.preprocessor, 'feature_names_in_'):
                expected_cols = self.preprocessor.feature_names_in_
                for col in expected_cols:
                    if col not in df_raw.columns:
                        df_raw[col] = 0
                
                df_raw = df_raw[expected_cols]

            X_processed = self.preprocessor.transform(df_raw)

            stage1_pred = self.stage1_model.predict(X_processed)[0]
            stage1_proba = self.stage1_model.predict_proba(X_processed)[0, 1]

            if stage1_pred == 0:
                return {
                    **meta_data, 
                    "label": "Normal", 
                    "attack_type": "--", 
                    "priority": "None", 
                    "risk_score": 0.0
                }

            stage2_proba_all = self.stage2_model.predict_proba(X_processed)
            stage2_pred_enc = np.argmax(stage2_proba_all, axis=1)
            raw_attack_type = self.cat_encoder.inverse_transform(stage2_pred_enc)[0]

            attack_type = CATEGORY_ABBREVIATION_MAP.get(raw_attack_type, raw_attack_type)
            category_confidence = np.max(stage2_proba_all)

            severity = SEVERITY_WEIGHTS.get(attack_type, 3)
            trust = stage1_proba * category_confidence
            risk_score = severity * trust
            priority = self.assign_priority_tier(risk_score)

            return {
                **meta_data,
                "label": "Attack",
                "attack_type": attack_type,
                "priority": priority,
                "risk_score": round(risk_score, 2)
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            return {**meta_data, "label": "Error", "risk_score": 0.0}

model_handler = MLModelHandler()