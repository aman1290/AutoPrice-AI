import os
from mlProject import logger
from mlProject.entity.config_entity import ModelTrainerConfig
import pandas as pd
from xgboost import XGBRegressor
import joblib



class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        train_data = pd.read_csv(self.config.train_data_path)
        test_data = pd.read_csv(self.config.test_data_path)

        train_x = train_data.drop([self.config.target_column], axis=1)
        test_x = test_data.drop([self.config.target_column], axis=1)
        train_y = train_data[[self.config.target_column]]
        test_y = test_data[[self.config.target_column]]

        # Initialize XGBoost regressor with parameters from config
        xgb = XGBRegressor(
            n_estimators=300,  # You can add these to your config if needed
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        
        xgb.fit(train_x, train_y.values.ravel())  # XGBoost needs 1D array for y

# Save feature columns
        feature_names = list(train_x.columns)
        joblib.dump(feature_names, "artifacts/data_transformation/feature_names.pkl")

        joblib.dump(xgb, os.path.join(self.config.root_dir, self.config.model_name))