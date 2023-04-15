from binance_trade_bot.strategies.default_strategy import Strategy
from .common import do_user_config, initialize_database_and_mock_manager  # type: ignore


class TestStrategy:

    def test_initialize(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager
        trade = Strategy(manager, db, logger, config)
        trade.initialize()
        assert True

    def test_scout(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager
        trade = Strategy(manager, db, logger, config)
        trade.initialize()
        trade.initialize_current_coin()
        trade.scout()
        assert True

    def test_bridge_scout(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager
        trade = Strategy(manager, db, logger, config)
        trade.initialize()
        trade.initialize_current_coin()
        trade.bridge_scout()
        assert True

    def test_initialize_current_coin(self, do_user_config, initialize_database_and_mock_manager):
        # test on run
        db, manager, logger, config = initialize_database_and_mock_manager
        trade = Strategy(manager, db, logger, config)
        trade.initialize()
        trade.initialize_current_coin()
        assert True
