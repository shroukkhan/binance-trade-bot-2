import datetime
import os
import pathlib
import shutil
from typing import Dict, List

import pytest
from binance import Client
from sqlitedict import SqliteDict

from binance_trade_bot.backtest import MockBinanceManager, MockDatabase
from binance_trade_bot.binance_stream_manager import BinanceCache
from binance_trade_bot.config import Config
from binance_trade_bot.logger import Logger


def rm_rf(paths: List[pathlib.Path]):
    for path in paths:
        if path.exists():
            shutil.rmtree(path)


@pytest.fixture(autouse=True)
def infra(delete_ok=False, delete_ok_first=False, dirs=None):
    dirs = [pathlib.Path(directory) for directory in dirs or ["logs", "data", "config"]]

    if delete_ok_first:
        rm_rf(dirs)

    for path in dirs:
        path.mkdir(exist_ok=True)

    yield

    if delete_ok:
        rm_rf(dirs)


@pytest.fixture(scope="function")
def do_user_config():
    """
    CURRENT_COIN_SYMBOL:
    SUPPORTED_COIN_LIST: "XLM TRX ICX EOS IOTA ONT QTUM ETC ADA XMR DASH NEO ATOM DOGE VET BAT OMG BTT"
    BRIDGE_SYMBOL: USDT
    API_KEY: vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A
    API_SECRET_KEY: NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j
    SCOUT_SLEEP_TIME: 1
    TLD: com
    STRATEGY: default
    BUY_TIMEOUT: 0
    SELL_TIMEOUT: 0
    BUY_ORDER_TYPE: limit
    SELL_ORDER_TYPE: market
    """

    # os.environ['CURRENT_COIN'] = 'ETH'
    os.environ["CURRENT_COIN_SYMBOL"] = "ETH"

    os.environ["API_KEY"] = "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
    os.environ["API_SECRET_KEY"] = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
    # os.environ['CURRENT_COIN_SYMBOL'] = 'BTT'
    os.environ["SUPPORTED_COIN_LIST"] = "XLM TRX ICX EOS IOTA ONT QTUM ETC ADA XMR DASH NEO ATOM DOGE VET BAT OMG BTT"
    os.environ["BRIDGE_SYMBOL"] = "USDT"
    os.environ["SCOUT_SLEEP_TIME"] = "1"
    os.environ["TLD"] = "com"
    os.environ["STRATEGY"] = "default"
    os.environ["BUY_TIMEOUT"] = "0"
    os.environ["SELL_TIMEOUT"] = "0"
    os.environ["BUY_ORDER_TYPE"] = "limit"
    os.environ["SELL_ORDER_TYPE"] = "market"

    yield

@pytest.fixture()
def initialize_database_and_mock_manager():
    logger: Logger = Logger(logging_service="guliguli")
    config: Config = Config()
    sqlite_cache = SqliteDict("data/testtest_cache.db")

    db = MockDatabase(logger, config)
    db.create_database()
    db.set_coins(config.SUPPORTED_COIN_LIST)

    start_date: datetime = datetime.datetime(2021, 6, 1)
    start_balances: Dict[str, float] = dict()
    start_balances["XLM"] = 100
    start_balances["DOGE"] = 101
    start_balances["BTT"] = 102
    start_balances["BAD"] = 103
    start_balances["ADA"] = 123
    start_balances["EOS"] = 124
    start_balances["USDT"] = 1000

    manager = MockBinanceManager(
        Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET_KEY, tld=config.BINANCE_TLD),
        sqlite_cache,
        BinanceCache(),
        config,
        db,
        logger,
        start_date,
        start_balances,
    )

    yield db, manager, logger, config

    # manager.close()
    # db.close()
    sqlite_cache.close()


def test_common(infra):
    return
