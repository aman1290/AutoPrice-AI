import os
from mlProject import logger
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.impute import SimpleImputer
from mlProject.entity.config_entity import DataTransformationConfig


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def train_test_splitting(self):
        """Complete data transformation and splitting pipeline"""
        try:
            # 1. Load data
            data = pd.read_csv(self.config.data_path)
            logger.info(f"Original data shape: {data.shape}")

            # 2. Convert numeric columns
            numeric_cols = ['km_driven', 'engine', 'price', 'reg_year_int']
            for col in numeric_cols:
                data[col] = pd.to_numeric(data[col], errors='coerce')

            # 3. Handle null values
            logger.info("Handling null values")
            null_counts = data.isnull().sum()
            logger.info(f"Null values detected:\n{null_counts[null_counts > 0]}")
            
            data = data.dropna(subset=['price'])
            data['engine'] = data['engine'].fillna(data['engine'].mode()[0])
            data['km_driven'] = data['km_driven'].fillna(data['km_driven'].median())
            data['transmission'] = data['transmission'].fillna(data['transmission'].mode()[0])
            data['ownership'] = data['ownership'].fillna('Unknown')

            # 4. Clean data
            logger.info("Cleaning data")
            data['ownership'] = data['ownership'].map({
                'First Owner': 1, 'Second Owner': 2, 'Third Owner': 3,
                'Fourth Owner': 4, 'Fifth Owner': 5, 'Unknown': -1
            })
            
            model_split = data['model'].str.split(n=1, expand=True)
            data['model_base'] = model_split[0]
            data['variant'] = model_split[1].fillna('Standard')
            data['is_automatic'] = (data['transmission'] == 'Automatic').astype(int)

            # 5. Add features
            logger.info("Adding features")
            data['price_per_cc'] = data['price'] / data['engine']
            data['car_age'] = pd.Timestamp.now().year - data['reg_year_int']
            data['km_per_year'] = data['km_driven'] / data['car_age']
            data['age_group'] = pd.cut(
                data['car_age'],
                bins=[0, 3, 7, 12, float('inf')],
                labels=['New', 'Mid', 'Old', 'Vintage']
            )

            # 6. Split data
            train, test = train_test_split(data, test_size=0.25, random_state=42)
            
            # 7. Save results
            os.makedirs(self.config.root_dir, exist_ok=True)
            train_path = os.path.join(self.config.root_dir, "train.csv")
            test_path = os.path.join(self.config.root_dir, "test.csv")
            train.to_csv(train_path, index=False)
            test.to_csv(test_path, index=False)
            
            logger.info(f"Train shape: {train.shape}, Test shape: {test.shape}")
            return train_path, test_path
            
        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            raise e


