import time

import config


class Cache(object):

    def __init__(self):
        self.storage = config.dbr[config.db_crawler]

    def save(self, uid, info):
        raise NotImplementedError

    def check(self, uid):
        raise NotImplementedError

    def retrive(self, uid):
        raise NotImplementedError


class CacheFollowers(Cache):
    collection = "followers"

    def __init__(self):
        super().__init__()
        self.storage_followers = self.storage[self.collection]

    def save(self, uid, info):
        self.storage_followers.update_one(
            {"fid": uid},
            {"$set":
                {
                    "value": info.get("followers"),
                    "date": time.time()
                }
            },
            upsert=True
        )

    def check(self, uid):
        document = self.storage_followers.find_one({"fid": uid})
        if not document:
            return False
        else:
            if time.time() - document.get("date", 0) < 604800:
                return True
            else:
                return False

    def retrive(self, uid):
        document = self.storage_followers.find_one({"fid": uid})
        if not document:
            return -1
        else:
            return document.get("value")


class CacheShares(Cache):
    collection = "shares"

    def __init__(self):
        super().__init__()
        self.storage_shares = self.storage[self.collection]

    def save(self, link, info):
        self.storage_shares.update_one(
            {"link": link},
            {"$set":
                {
                    "value": info.get("shares"),
                    "date": time.time()
                }
            },
            upsert=True
        )

    def check(self, link):
        document = self.storage_shares.find_one({"link": link})
        if not document:
            return False
        else:
            if time.time() - document.get("date", 0) < 604800:  # 7 days
                return True
            else:
                return False

    def retrive(self, link):
        document = self.storage_shares.find_one({"link": link})
        if not document:
            return -1
        else:
            return document.get("value")
