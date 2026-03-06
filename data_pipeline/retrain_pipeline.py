"""Simple retraining pipeline for cron usage.

Example:
python data_pipeline/retrain_pipeline.py --symbol BTC-USD --timeframe 5m
"""

import argparse
from model.train import train


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', default='BTC-USD')
    parser.add_argument('--timeframe', default='5m')
    args = parser.parse_args()
    path = train(symbol=args.symbol, timeframe=args.timeframe)
    print(f'Retrained model: {path}')


if __name__ == '__main__':
    main()
