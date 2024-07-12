import mlflow
from prefect import flow, task, get_run_logger

from src.model import Model
from src.prepare_dataset import split_data, prepare_data, read_dataset
from constants import MODEL_DIR, MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME


@task
def read_dataset_task():
    df = read_dataset()
    return df


@task
def prepare_dataset_task(df, numeric_cols, target):
    X, y = prepare_data(df=df, numeric_cols=numeric_cols, target=target)
    return X, y


@task
def split_dataset_task(X, y, seed):
    X_train, X_val, y_train, y_val = split_data(X, y, test_size=0.2, random_state=seed)
    return X_train, X_val, y_train, y_val


@task
def create_model_task(numeric_cols, target):
    model = Model(numeric_cols=numeric_cols, target=target)
    return model


@task
def train_model_task(model, X, y):
    model.train_model(X, y)


@task
def calculate_accuracy_task(model, X, y):
    score = model.get_accuracy(X, y)
    return score


@task
def save_model_task(model, model_dir):
    model.save(model_dir)


@flow
def train_simple_flow(numeric_cols, seed=565):
    target = "Fire Alarm"
    numeric_cols = sorted(numeric_cols)

    logger = get_run_logger()

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run() as curr_run:
        logger.info(f"started mlflow run: {curr_run.info.run_name}")

        mlflow.log_param("seed", seed)
        mlflow.log_param("numeric_cols", numeric_cols)

        df = read_dataset_task()

        X, y = prepare_dataset_task(
            df=df,
            numeric_cols=numeric_cols,
            target=target,
        )

        X_train, X_val, y_train, y_val = split_dataset_task(
            X=X,
            y=y,
            seed=seed,
        )

        logger.info(f"Training data shape(X,y): {X_train.shape}, {y_train.shape}")
        logger.info(f"Validation data shape(X,y): {X_val.shape}, {y_val.shape}")

        mlflow.log_param("training data shapes", f"{X_train.shape, y_train.shape}")
        mlflow.log_param("validation data shapes", f"{X_val.shape, y_val.shape}")

        model = create_model_task(numeric_cols=numeric_cols, target=target)
        logger.info(f"starting training using {X_train.shape[0]} examples")
        train_model_task(model, X_train, y_train)
        logger.info("training ended")

        score = calculate_accuracy_task(model, X_train, y_train)
        logger.info(f"Training Accuracy: {score:.4f}")
        mlflow.log_metric("train_acc", score)

        score = calculate_accuracy_task(model, X_val, y_val)
        logger.info(f"Validation Accuracy: {score:.4f}")
        mlflow.log_metric("val_acc", score)

        logger.info("Saving model artifacts")
        save_model_task(model, MODEL_DIR)
        logger.info(f"Model artifacts saved to {MODEL_DIR}")

        mlflow.log_artifacts(local_dir=MODEL_DIR, artifact_path="model")


@flow
def feature_selection_flow(numeric_cols_list: list):
    logger = get_run_logger()
    for i, numeric_cols in enumerate(numeric_cols_list):
        assert isinstance(numeric_cols, list)
        numeric_cols = sorted(numeric_cols)

        logger.info(
            (
                f"{i+1}/{len(numeric_cols_list)} running "
                f"training_flow with numeric_cols: {numeric_cols}"
            )
        )

        train_simple_flow(numeric_cols=numeric_cols)


if __name__ == "__main__":
    seed = 565
    numeric_cols = ["Temperature[C]", "Humidity[%]"]

    train_simple_flow(
        numeric_cols=numeric_cols,
        seed=seed,
    )
