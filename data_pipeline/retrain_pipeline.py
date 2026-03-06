"""Simple retraining pipeline: train model and run a smoke backtest."""

import subprocess


def run():
    subprocess.run(["python", "model/train.py"], check=True)
    subprocess.run(["python", "model/backtest.py"], check=True)


if __name__ == "__main__":
    run()
