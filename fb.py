import csv
import datetime
import os
import time

import client
import output


class FacebookCrawler(object):

    def __init__(self, file, output_path, timedelta=None):
        self.file = file
        self.output_path = output_path
        self.output = output.Output(output_path, "|")
        self.parser_account = client.AccountParser(timedelta)
        self.parser_account_info = client.PagesFacebook(timedelta)
        self.parser_keywords = client.GraphParser(timedelta)

    def run_keywords(self):
        default_fields = {
            "delivered_date": datetime.date.isoformat(datetime.datetime.now())
        }

        listdir = os.listdir(self.output_path)
        with open(self.file, "r", encoding="utf-8") as csvfile:
            userset = csv.reader(
                csvfile,
                delimiter=","
            )
            self.parser_keywords.login()
            userset.__next__()
            for user in userset:
                account_id = user[0]
                category_id = user[1]
                folder_name = user[2]
                query_raw = user[3]
                query = user[3].split(",")
                keywords = []
                excluded = []

                print(f"\n********\nQUERY: {query}")
                qf = []
                for q in query:
                    if "#" in q:
                        qf.append(q.replace("#", "%23"))
                    else:
                        qf.append(q)
                query = qf[:]

                if f"{category_id}.csv" in listdir:
                    continue

                default_fields.update({
                    "account_id": account_id,
                    "category_id": category_id,
                    "category_name": folder_name,
                    "keywords": keywords if keywords else query_raw
                })

                response = self.parser_keywords.search(
                    query,
                    keywords=keywords,
                    excluded=excluded,
                    comments=False,
                    iter_depth_posts=8,
                    iter_depth_comments=10
                )

                self.output.save(
                    category_id,
                    response,
                    default_fields,
                    self.output_path
                )

                yield response
                print(f"\nEND: {query} \n********\n")

    def run_accounts(self):
        default_fields = {
            "delivered_date": datetime.date.isoformat(datetime.datetime.now())
        }

        listdir = os.listdir(self.output_path)
        with open(self.file, "r", encoding="utf-8") as csvfile:
            userset = csv.reader(
                csvfile,
                delimiter=","
            )
            # self.parser_keywords.login()
            self.parser_account.login()
            userset.__next__()
            for user in userset:
                account_id = user[0]
                category_id = user[1]
                folder_name = user[2]
                query_raw = user[3]
                query = user[3].split(",")
                keywords = []
                excluded = []

                print(f"\n********\nQUERY: {query}")
                qf = []
                for q in query:
                    if "#" in q:
                        qf.append(q.replace("#", "%23"))
                    else:
                        qf.append(q)
                query = qf[:]

                if f"{category_id}.csv" in listdir:
                    continue

                default_fields.update({
                    "account_id": account_id,
                    "category_id": category_id,
                    "category_name": folder_name,
                    "keywords": keywords if keywords else query_raw
                })

                try:
                    response = self.parser_account.search(
                        query,
                        keywords=keywords,
                        excluded=excluded,
                    )
                except Exception:
                    continue

                self.output.save(
                    category_id,
                    response,
                    default_fields,
                    self.output_path
                )

                yield response
                print(f"\nEND: {query} \n********\n")


if __name__ == "__main__":
    ipath = "input/21_end-kol_mom_bloggers.csv"
    opath = "output/21_end-kol_mom_bloggers/"
    timedelta = (
        datetime.datetime(2010, 5, 29, 0, 0, 0),  # 2010
        datetime.datetime(2020, 5, 30, 23, 59, 59)  # 2020
    )
    scanner = FacebookCrawler(
        ipath,
        opath,
        timedelta=timedelta
    )

    i = 0

    for res in scanner.run_accounts():
        time.sleep(5)
    output.csv_compressor(poutput=opath)
