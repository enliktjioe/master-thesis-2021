from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings class to store training parameters. Set this before running the train

    """

    NUM_LABELS: int = 23  # Number of Labels in the dataset
    MAX_LEN: int = 64  # Tokenizer max length
    TRAIN_BATCH_SIZE: int = 8  # Training Batch size
    VALID_BATCH_SIZE: int = 4  # Validation/Testing Batch size
    EPOCHS: int = 10  # Number of epochs
    LEARNING_RATE: int = 1e-05

    PRE_TRAINED_MODEL: str = "bert-base-uncased"  # Bert pre trained model name
    DEVICE: str = "cpu"

    MODEL_DIR: str = "model_files/original"  # Folder name to store all files
    MODEL_NAME: str = "bert-topic-sentiment.bin"  # Output model name
    MODEL_NAME_COLAB: str = "bert-topic-sentiment-colab-final.bin"  # Pre trained final model

    LOSS_FUN: str = "BCE"  # 'BCE' or 'focal'

    # CSV_INPUT: str = "bolt_apple_appstore_review.csv"
    
    # bolt_google_playstore_review.csv 17MB (21 Dec 2020)
    CSV_INPUT: str = "https://drive.google.com/file/d/1qWuyf3UrpaU5xnxLmO3GMFa6zybSFYQh/view?usp=sharing"
    # USE_COLS: list = ['content','at']
    USE_COLS: list = ['content']
