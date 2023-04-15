import pytest

from binance_trade_bot.auto_trader import AutoTrader
from binance_trade_bot.ratios import CoinStub
from .common import do_user_config, initialize_database_and_mock_manager  # type: ignore


class StubAutoTrader(AutoTrader):
    def scout(self):
        return


class TestAutoTrader:

    def test_initialize(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager
        autotrader = StubAutoTrader(manager, db, logger, config)
        autotrader.initialize()
        assert True

    def test_transaction_through_bridge(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)

        coinfrom = CoinStub.get_by_symbol('XLM')
        cointo = CoinStub.get_by_symbol('EOS')

        sell_price = autotrader.manager.get_ticker_price('XLMUSDT')
        buy_price = autotrader.manager.get_ticker_price('EOSUSDT')

        autotrader.transaction_through_bridge(coinfrom, cointo, sell_price, buy_price)
        assert True

    # TODO: Check set matrix + breaks
    @pytest.mark.parametrize("coin_symbol", [['XLM', 'EOS']])
    def test_update_trade_threshold(self, do_user_config, initialize_database_and_mock_manager, coin_symbol):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)

        to_coin = CoinStub.get_by_symbol(coin_symbol[1])
        to_coin_price = autotrader.manager.get_ticker_price(to_coin.symbol + config.BRIDGE.symbol)
        from_coin = CoinStub.get_by_symbol(coin_symbol[0])
        from_coin_price = autotrader.manager.get_ticker_price(from_coin.symbol + config.BRIDGE.symbol)
        '''
        In the Binance order API, cumulativeQuoteQty represents the total amount of quote asset 
        that has been traded for the given order.

        For example, if you place a sell order for 1 BTC at a price of 50,000 USDT per BTC, the
        cumulativeQuoteQty will initially be 0. As the order is partially or fully filled, the
        cumulativeQuoteQty will be updated to reflect the total amount of USDT that has been 
        received in exchange for the sold BTC.

        cumulativeQuoteQty is useful for tracking the progress of an order and determining the 
        total value of a trade. It is important to note that cumulativeQuoteQty is denominated
         in the quote asset (e.g., USDT), not the base asset (e.g., BTC).
        '''
        cumulative_quote_qty = autotrader.manager.get_currency_balance(config.BRIDGE.symbol) \
                               + autotrader.manager.get_currency_balance(to_coin.symbol) * from_coin_price

        to_coin_amount = autotrader.manager.get_currency_balance(to_coin.symbol) + cumulative_quote_qty / to_coin_price

        res = autotrader.update_trade_threshold(
            to_coin=to_coin,
            from_coin=from_coin,
            to_coin_buy_price=to_coin_price,
            to_coin_amount=to_coin_amount,
            quote_amount=cumulative_quote_qty)
        assert res

    # TODO: Why time.sleep(1)?
    # TODO: balanses[XXX] = None ! -1
    def test__max_value_in_wallet(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)
        res = autotrader._max_value_in_wallet()
        print(f'_wallet {res}')
        assert True

        # bridge_balance = autotrader.manager.get_currency_balance(autotrade.config.BRIDGE.symbol)
        # assert res == bridge_balance

    def test_initialize_trade_thresholds(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)
        res = autotrader.initialize_trade_thresholds()
        assert res

    def test_scout(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)
        autotrader.scout()
        assert True  # this shit does nothing :/

    @pytest.mark.parametrize("coin_symbol", ['XLM', 'DOGE'])
    def test_get_ratios(self, do_user_config, initialize_database_and_mock_manager, coin_symbol):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        from_coin = CoinStub.get_by_symbol(coin_symbol)
        autotrader = StubAutoTrader(manager, db, logger, config)
        
        manager = autotrader.manager
        from_coin_amount = manager.get_currency_balance(from_coin.symbol)
        from_coin_price, from_coin_quote = manager.get_market_sell_price(
            from_coin.symbol + manager.config.BRIDGE.symbol, from_coin_amount
        )
        ratio_dict, price_amounts = autotrader._get_ratios(from_coin, from_coin_price, from_coin_quote)
        # print('\n_get_ratios:', ratio_dict, '\n', price_amounts)
        assert True

        # test on calculation. Calculate on first free coin (to_coin).

        to_coin = CoinStub.get_by_idx(0 if from_coin.idx != 0 else 1)

        ## Initial values for assert. Sell price & ratio
        quote_amount = 10000
        coin_sell_price = autotrader.manager.get_ticker_price(from_coin.symbol + autotrader.config.BRIDGE.symbol)
        ratio_dict, price_amounts = autotrader._get_ratios(from_coin, coin_sell_price, quote_amount)

        ## Calculation (???) & asserts
        ratio = (autotrader.db.ratios_manager.get_from_coin(from_coin.idx))[to_coin.idx]  # 1 element from <coin> array

        ratio_dict_to_coin = ratio_dict[(from_coin.idx, to_coin.idx)]  # 1 element from <coin> array
        price_amounts_to_coin = price_amounts[to_coin.symbol]  # 1 element from <coin> array

        optional_coin_buy_price, optional_coin_amount = autotrader.manager.get_market_buy_price(
            to_coin.symbol + autotrader.config.BRIDGE.symbol,
            quote_amount)
        assert optional_coin_buy_price == price_amounts_to_coin[0]
        assert optional_coin_amount == price_amounts_to_coin[1]

        coin_opt_coin_ratio = coin_sell_price / optional_coin_buy_price

        transaction_fee = autotrader.manager.get_fee(from_coin.symbol, autotrader.config.BRIDGE.symbol, True) + \
                          autotrader.manager.get_fee(to_coin.symbol, autotrader.config.BRIDGE.symbol, False)
        
        #TODO: Change this to scout margin 
        # # This is main ratio's elupopa :)
        # assert (coin_opt_coin_ratio - transaction_fee *
        #        autotrader.config.SCOUT_MULTIPLIER * coin_opt_coin_ratio) - ratio == ratio_dict_to_coin

    @pytest.mark.parametrize("coin_symbol", ['XLM', 'DOGE'])
    def test_jump_to_best_coin(self, do_user_config, initialize_database_and_mock_manager, coin_symbol):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        from_coin = CoinStub.get_by_symbol(coin_symbol)
        autotrader = StubAutoTrader(manager, db, logger, config)
        manager = autotrader.manager

        # from_coin_price = manager.get_ticker_price(coin_symbol + 'USDT') # same stuff we get from get_market_sell_price 
        from_coin_amount = manager.get_currency_balance(from_coin.symbol)
        from_coin_price, from_coin_quote = manager.get_market_sell_price(
            from_coin.symbol + manager.config.BRIDGE.symbol, from_coin_amount
        )
        autotrader._jump_to_best_coin(from_coin, from_coin_price, from_coin_price, from_coin_quote)
        assert True

    # TODO: Check return coin & None
    def test_bridge_scout(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)

        pusher = [];
        pusher.append(autotrader.manager.balances[autotrader.config.BRIDGE.symbol])

        autotrader.manager.balances[autotrader.config.BRIDGE.symbol] = -1
        res = autotrader.bridge_scout()
        assert res is None

        autotrader.manager.balances[autotrader.config.BRIDGE.symbol] = pusher.pop()

        if 0:  # Why v<0? v<0 always.

            pricer = {}

            bridge_balance = autotrader.manager.get_currency_balance(autotrader.config.BRIDGE.symbol)

            for coin in CoinStub.get_all():
                if coin.symbol not in autotrader.manager.balances.keys():
                    continue
                if (autotrader.manager.balances[coin.symbol] > 0.0) and (coin != autotrader.config.BRIDGE):
                    current_coin_price = autotrader.manager.get_ticker_price(
                        coin.symbol + autotrader.config.BRIDGE.symbol)
                    pricer[coin.symbol] = current_coin_price
                    min_notional = autotrader.manager.get_min_notional(coin.symbol, autotrader.config.BRIDGE.symbol)
                    print('\n', coin, min_notional)
                    ratio_dict, _ = autotrader._get_ratios(coin, current_coin_price, bridge_balance)
                    print([v > 0.0 for v in ratio_dict.values()])
                    print(coin, current_coin_price, bridge_balance, ratio_dict)

            print(pricer)

    def test_update_values(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager

        autotrader = StubAutoTrader(manager, db, logger, config)

        autotrader.update_values()
        assert True
