import pytest

from binance_trade_bot.config import Config


def config_test():
    params = dict()

    params["CURRENT_COIN"] = "ETH"
    params["CURRENT_COIN_SYMBOL"] = "ETH"
    params["SUPPORTED_COIN_LIST"] = "XLM TRX ICX EOS IOTA ONT QTUM ETC ADA XMR DASH NEO ATOM DOGE VET BAT OMG BTT"
    params["BRIDGE_SYMBOL"] = "USDT"
    #######params['BRIDGE'] = 'USDT'  ## ??????????

    params["API_KEY"] = "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
    params["API_SECRET_KEY"] = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"

    params["SCOUT_SLEEP_TIME"] = "1"

    params["TLD"] = "com"
    params["STRATEGY"] = "default"
    params["ENABLE_PAPER_TRADING"] = "False"
    params["HOURS_TO_KEEP_SCOUTING_HISTORY"] = "10.0"

    # params['BUY_TIMEOUT']  = "0"
    # params['SELL_TIMEOUT'] = "0"
    # params['BUY_ORDER_TYPE'] = 'limit'
    # params['SELL_ORDER_TYPE'] = 'market'

    return params


@pytest.fixture(scope="function")
def do_user_config_env(monkeypatch):
    params = config_test()
    for key, val in params.items():
        monkeypatch.setenv(key, val)


def test_config_no_supported_coin_list_in_env(do_user_config_env, monkeypatch):
    monkeypatch.delenv("SUPPORTED_COIN_LIST")
    config = Config()
    assert len(config.SUPPORTED_COIN_LIST) > 0, "SUPPORTED_COIN_LIST should not be empty"
    # read supported coin list from file into a list
    with open("supported_coin_list", "r") as f:
        supported_coin_list = f.read().splitlines()
    assert config.SUPPORTED_COIN_LIST == supported_coin_list, "SUPPORTED_COIN_LIST should be read from file"


def test_config_on_run(do_user_config_env):
    config = Config()
    params = config_test()

    for ikey in params:
        mustvalue = params[ikey]
        if ikey == "CURRENT_COIN":
            ikey = "CURRENT_COIN_SYMBOL"
        if ikey == "API_KEY":
            ikey = "BINANCE_API_KEY"
        if ikey == "API_SECRET_KEY":
            ikey = "BINANCE_API_SECRET_KEY"
        if ikey == "TLD":
            ikey = "BINANCE_TLD"
        if ikey == "HOURS_TO_KEEP_SCOUTING_HISTORY":
            ikey = "SCOUT_HISTORY_PRUNE_TIME"

        getvalue = getattr(config, ikey)

        if ikey == "SUPPORTED_COIN_LIST":
            getvalue = " ".join(getvalue)
        if ikey == "SCOUT_SLEEP_TIME":
            mustvalue = int(mustvalue)

        if ikey == "SCOUT_HISTORY_PRUNE_TIME":
            mustvalue = float(mustvalue)
        if ikey == "ENABLE_PAPER_TRADING":
            mustvalue = not (mustvalue == "0" or mustvalue.upper())

        # if ikey=='BUY_ORDER_TYPE'      : mustvalue = mustvalue.upper()
        # if ikey=='SELL_ORDER_TYPE'     : mustvalue = mustvalue.upper()
        # if ikey=='BRIDGE'              : mustvalue = Coin(mustvalue, False)
        if ikey == "BRIDGE":
            continue  # probably compute field from BRIDGE_SYMBOL

        assert (
                mustvalue == getvalue
        ), f"Config values and input values not compare for {ikey}, must be {mustvalue}, get {getvalue}"
