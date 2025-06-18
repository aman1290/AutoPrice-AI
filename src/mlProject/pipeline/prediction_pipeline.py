import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class PredictionPipeline:
    def __init__(self):
        # Load model and encoders using pathlib
        self.model = joblib.load(Path('artifacts/model_trainer/model.joblib'))
        self.model_encoder = joblib.load(Path("artifacts/data_transformation/model_encoder.pkl"))
        self.ohe = joblib.load(Path("artifacts/data_transformation/ohe_encoder.pkl"))
        self.feature_names = joblib.load(Path("artifacts/data_transformation//feature_names.pkl"))
        # Define mappings
        self.ownership_map = {
            'First Owner': 1,
            'Second Owner': 2,
            'Third Owner': 3,
            'Fourth Owner': 4
        }
        self.transmission_map = {
            'Manual': 0,
            'Automatic': 1
        }

    def preprocess_input(self, raw_dict):
        df = pd.DataFrame([raw_dict])

    # Step 0: Rename & derive to match training
        df['reg_year_int'] = df['year']
        df['km_driven'] = df['kms_driven']
        df['car_age'] = 2025 - df['year']
        df.drop(['year', 'kms_driven'], axis=1, inplace=True)

    # Step 1: Apply mappings
        df['ownership'] = df['ownership'].map(self.ownership_map)
        df['transmission'] = df['transmission'].map(self.transmission_map)

    # Step 2: Model encoding
        df['model_encoded'] = self.model_encoder.transform(df['model'])

    # Step 3: One-hot encode
        ohe_columns = ['make', 'fuel', 'city']
        df_ohe = pd.DataFrame(
        self.ohe.transform(df[ohe_columns]),
        columns=self.ohe.get_feature_names_out(ohe_columns),
        index=df.index
        )

    # Step 4: Final dataframe
        df_final = pd.concat([
        df.drop(columns=['model'] + ohe_columns),
        df_ohe
        ], axis=1)

        df_final = df_final.reindex(columns=self.feature_names, fill_value=0)

        return df_final


    def predict(self, raw_dict):
        input_df = self.preprocess_input(raw_dict)
        prediction = self.model.predict(input_df)[0]
        return np.round(prediction, 2)

'''
pipeline = PredictionPipeline()

sample_input = {
   
  "make": "Maruti",
  "model": "Brezza Zxi",
  "kms_driven": 38000,
  "ownership": "First Owner",
  "transmission": "Manual",
  "engine": 1462,
  "fuel": "Petrol",
  "city": "Hyderabad",
  "year": 2023
  


}


predicted_price = pipeline.predict(sample_input)
print(f"Predicted Price: ₹{predicted_price:,}")
'''