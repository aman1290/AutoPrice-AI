import os
from mlProject import logger
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.impute import SimpleImputer
from mlProject.entity.config_entity import DataTransformationConfig
import category_encoders as ce
from sklearn.preprocessing import OneHotEncoder
import joblib

class DataTransformation:
    def __init__(self, config):
        self.config = config
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

    def _preprocess_data(self, data):
        """Apply initial preprocessing to data"""
        # Convert mappings
        data['ownership'] = data['ownership'].map(self.ownership_map)
        data['transmission'] = data['transmission'].map(self.transmission_map)
        return data

    def train_test_splitting(self):
        """Complete data transformation pipeline with leakage prevention"""
        try:
            # Load data
            data = pd.read_csv(self.config.data_path)
            logger.info(f"Original data shape: {data.shape}")

            # Initial split to prevent leakage
            train, test = train_test_split(
                data,
                test_size=self.config.test_size,
                random_state=self.config.random_state
            )
            logger.info(f"Initial split - Train: {train.shape}, Test: {test.shape}")

            # Apply base preprocessing
            train = self._preprocess_data(train)
            test = self._preprocess_data(test)

            # Target encoding for 'model'
            model_encoder = ce.TargetEncoder(cols=['model'], smoothing=5.0)
            model_encoder.fit(train['model'], train['price'])
            train['model_encoded'] = model_encoder.transform(train['model'])
            test['model_encoded'] = model_encoder.transform(test['model'])

            # One-hot encoding for other categorical features
            ohe_columns = ['make', 'fuel', 'city']
            ohe = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
            ohe.fit(train[ohe_columns])
            
            # Transform features
            train_ohe = pd.DataFrame(
                ohe.transform(train[ohe_columns]),
                columns=ohe.get_feature_names_out(ohe_columns),
                index=train.index
            )
            test_ohe = pd.DataFrame(
                ohe.transform(test[ohe_columns]),
                columns=ohe.get_feature_names_out(ohe_columns),
                index=test.index
            )
            
            # Combine encoded data
            train = pd.concat([
                train.drop(columns=['model'] + ohe_columns),
                train_ohe
            ], axis=1)
            
            test = pd.concat([
                test.drop(columns=['model'] + ohe_columns),
                test_ohe
            ], axis=1)

            # Save processed data
            os.makedirs(self.config.root_dir, exist_ok=True)
            train_path = os.path.join(self.config.root_dir, "train.csv")
            test_path = os.path.join(self.config.root_dir, "test.csv")
            train.to_csv(train_path, index=False)
            test.to_csv(test_path, index=False)
            joblib.dump(model_encoder, os.path.join(self.config.root_dir, "model_encoder.pkl"))
            joblib.dump(ohe, os.path.join(self.config.root_dir, "ohe_encoder.pkl"))

            logger.info(f"Final train shape: {train.shape}, test shape: {test.shape}")
            logger.info(f"Processed data saved to {self.config.root_dir}")
            return train_path, test_path

        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            raise
