import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import mlflow

from prefect import task,flow, get_run_logger

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("homework3")
mlflow.sklearn.autolog()

@task
def read_data(path):
    df = pd.read_parquet(path)
    return df
@task
def prepare_features(df, categorical, train=True):
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    mean_duration = df.duration.mean()
    if train:
        print(f"The mean duration of training is {mean_duration}")
    else:
        print(f"The mean duration of validation is {mean_duration}")
    
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df
@task
def train_model(df, categorical):
    with mlflow.start_run():
        train_dicts = df[categorical].to_dict(orient='records')
        dv = DictVectorizer()
        X_train = dv.fit_transform(train_dicts) 
        y_train = df.duration.values

        print(f"The shape of X_train is {X_train.shape}")
        print(f"The DictVectorizer has {len(dv.feature_names_)} features")

        lr = LinearRegression()
        lr.fit(X_train, y_train)
        y_pred = lr.predict(X_train)
        mse = mean_squared_error(y_train, y_pred, squared=False)
        mlflow.log_metric("mse", mse)
        print(f"The MSE of training is: {mse}")
    return lr, dv
@task
def run_model(df, categorical, dv, lr):
    val_dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(val_dicts) 
    y_pred = lr.predict(X_val)
    y_val = df.duration.values

    mse = mean_squared_error(y_val, y_pred, squared=False)
    print(f"The MSE of validation is: {mse}")
    return

from time import strftime
from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import IntervalSchedule
from prefect.flow_runners import SubprocessFlowRunner
from datetime import timedelta
import pickle


@task
def get_paths(date):
    print(date, "get_paths date")
    if date == None:
        print(date, "if date")
        train_path = "./data/fhv_tripdata_2021-01.parquet"
        val_path= "./data/fhv_tripdata_2021-02.parquet"
        print(val_path, train_path)
        print("None, Today!")
    else:
        train_path= "./data/fhv_tripdata_2021-06.parquet"
        val_path = "./data/fhv_tripdata_2021-07.parquet"
        print("Not none!")
        print(train_path, val_path)
    return train_path, val_path

@flow
def main(date="2021-08-15"):
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    logger = get_run_logger()
    train_path, val_path= get_paths(date).result()
    categorical = ['PUlocationID', 'DOlocationID']

    df_train = read_data(train_path)
    df_train_processed = prepare_features(df_train, categorical)

    df_val = read_data(val_path)
    df_val_processed = prepare_features(df_val, categorical, False)

    # train the model
    lr, dv = train_model(df_train_processed, categorical).result()
    run_model(df_val_processed, categorical, dv, lr)
    logger.info(f"model-{date}.bin")
    with open(f"./models/model-{date}.bin", 'wb') as f_out: 
        pickle.dump((lr), f_out)

    logger.info(f"dv-{date}.bin")
    with open(f"./models/dv-{date}.bin", 'wb') as f_out: 
        pickle.dump((dv), f_out)
        

from prefect.orion.schemas.schedules import CronSchedule
DeploymentSpec(
    flow=main,
    name="model_training",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    flow_runner=SubprocessFlowRunner(),
    tags=["ml"],
)



#DeploymentSpec(
    #flow = main,
    #name="cron_hw",
    #flow_runner=SubprocessFlowRunner(),
    #schedule=CronSchedule(
        #cron="0 9 15 * *")

    #)