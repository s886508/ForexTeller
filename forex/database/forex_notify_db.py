# -*- coding: utf-8 -*-
from tinydb import TinyDB, Query

class ForexNotifyDB:

    def __init__(self, db_path = "notify.json"):
        self.__db = TinyDB(db_path)
        self.__query = Query()

    def __del__(self):
        self.__db.close()

    def add(self, user_id, cond, price):
        """ Insert/Update record to database

        :param user_id:
        :param cond(str): Currency to notify.
        :param price(float): Currency price to notify.
        :return Return True if insert or update record successfully
        """
        if type(price) is not float or type(cond) is not str:
            print("Cannot insert the record to database")
            return False

        if self.__db is None:
            print("Database cannot be opened.")
            return False

        query_data = self.__db.search((self.__query.user_id == user_id) & (self.__query.cond == cond))
        if len(query_data) > 0:
            for data in query_data:
                data["price"] = price
            self.__db.write_back(query_data)
        else:
            self.__db.insert({"user_id": user_id, "cond": cond, "price": price})

        return True

    def remove(self, user_id, cond):
        """ Remove record from opened database.

        :param user_id
        :param cond(str): Currency to notify.
        """
        if self.__db is not None:
            self.__db.remove((self.__query.user_id == user_id) & (self.__query.cond == cond))

    def get_all_data(self):
        """ Return all records from opened database. """
        if self.__db is not None:
            return self.__db.all()
        return None

    def clear(self):
        for record in self.get_all_data():
            self.__db.remove(self.__query.user_id == record["user_id"])