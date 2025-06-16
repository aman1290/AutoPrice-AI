from mlProject.constants import*
from mlProject.utils.common import read_yaml, create_directories 
from mlProject.entity.config_entity import (DataIngestionConfig ,DataValidationConfig,DataTransformationConfig,ModelTrainerConfig)
from mlProject import logger

class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH,
        schema_filepath = SCHEMA_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        create_directories([self.config.artifacts_root])


    
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir 
        )

        return data_ingestion_config
    

    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        schema = self.schema.COLUMNS

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=config.root_dir,
            STATUS_FILE=config.STATUS_FILE,
            unzip_data_dir = config.unzip_data_dir,
            all_schema=schema,
        )

        return data_validation_config
    
    
    
    def get_data_transformation_config(self) -> DataTransformationConfig:
        try:
            # Verify config sections exist
            if not hasattr(self.config, 'data_transformation'):
                raise ValueError("Missing 'data_transformation' in config")
            if not hasattr(self.schema, 'TARGET_COLUMN'):
                raise ValueError("Missing 'TARGET_COLUMN' in schema")

            config = self.config.data_transformation
            schema = self.schema.TARGET_COLUMN

            # Set default params if not specified
            target_encode_cols = getattr(self.params, 'target_encode_cols', ["model"])
            test_size = getattr(self.params, 'test_size', 0.25)
            random_state = getattr(self.params, 'random_state', 42)

            create_directories([config.root_dir])

            return DataTransformationConfig(
                root_dir=config.root_dir,
                data_path=config.data_path,
                target_column=schema.name,
                target_encode_cols=target_encode_cols,
                test_size=test_size,
                random_state=random_state
            )
        except Exception as e:
            logger.error(f"Failed to create data transformation config: {str(e)}")
            raise



    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer
        params = self.params.Xgboost
        schema =  self.schema.TARGET_COLUMN

        create_directories([config.root_dir])

        model_trainer_config = ModelTrainerConfig(
            root_dir=config.root_dir,
            train_data_path = config.train_data_path,
            test_data_path = config.test_data_path,
            model_name = config.model_name,
            params= params,
            target_column = schema.name
            
        )

        return model_trainer_config