# -*- coding: utf-8 -*-
import os
from forex.database.forex_notify_db import ForexNotifyDB

db_name = "test.json"

class TestDataBase(object):

    def test_creat_db(self):
        db = ForexNotifyDB(db_name)
        assert os.path.exists(db_name)

        db = None
        os.remove(db_name)

    def test_add_data(self):
        db = ForexNotifyDB(db_name)

        # Case 1: Normal
        db.add(0, "test", 30.0)
        record = db.get_all_data()
        assert record[0]["user_id"] == 0
        assert record[0]["cond"] == "test"
        assert record[0]["price"] == 30.0

        # Case 2: Invalid price type
        ret = db.add(0, "test", "30.0")
        assert ret == False

        # Case 2: Invalid key type
        ret = db.add(0, 30, "30.0")
        assert ret == False

        # Case 4: Update data
        db.add(0, "test", 29.0)
        record = db.get_all_data()
        assert record[0]["user_id"] == 0
        assert record[0]["cond"] == "test"
        assert record[0]["price"] == 29.0

        db = None
        os.remove(db_name)

    def test_remove_data(self):
        db = ForexNotifyDB(db_name)

        db.add(0, "test", 30.0)
        record = db.get_all_data()
        assert record[0]["user_id"] == 0
        assert record[0]["cond"] == "test"
        assert record[0]["price"] == 30.0

        db.remove(0, "test1")
        record = db.get_all_data()
        assert len(record) == 1

        db.remove(0, "test")
        record = db.get_all_data()
        assert len(record) == 0

        db = None
        os.remove(db_name)

    def test_clear_data(self):
        db = ForexNotifyDB(db_name)

        db.add(0, "test", 30.0)
        db.add(0, "test2", 31.0)
        assert len(db.get_all_data()) == 2

        db.clear()
        assert len(db.get_all_data()) == 0

        db = None
        os.remove(db_name)