import csv
import datetime
import os

import config


class Output(object):

    def __init__(self, path, delimiter):
        self.path = path
        self.delimiter = ","

    def save(self, fname, results, defaultfields, writeheader=True):
        with open(f"{self.path}{fname}.csv", "a", encoding="utf-8") as csvfile:
            postwriter = csv.DictWriter(
                csvfile,
                fieldnames=config.fieldnames_output,
                delimiter=self.delimiter
            )
            if writeheader:
                postwriter.writeheader()

            for post in results:

                print("POST: ", post)
                if defaultfields:
                    post.update(defaultfields)
                try:
                    del post["_id"]
                except KeyError:
                    pass
                postwriter.writerow(post)


def csv_compressor(poutput="output/KMCIC/"):

    now = datetime.datetime.now()
    fname = "facebook_{}{:02d}{:02d}0000.csv".format(now.year, now.month, now.day)
    files = os.listdir(f"{poutput}")

    with open(f"/home/purusah/Desktop/{fname}", "w", encoding="utf-8") as fres:
        frescsv = csv.DictWriter(
            fres,
            fieldnames=config.fieldnames_output,
            delimiter=","
        )
        frescsv.writeheader()
        for file in files:
            with open(f"{poutput}{file}", "r", encoding="utf-8") as f:
                csvreader = csv.DictReader(
                    f,
                    delimiter=","
                )
                for row in csvreader:
                    try:
                        sample = dict(row)
                        if sample.get("post_type") == "post":
                            name = sample.get("author_id")
                            link = sample.get("link")
                            print(f"{name} {link}")
                            if name.startswith("/"):
                                print(f"AUTHORID: {name}")
                                endposition = name.find("?")
                                name = name[1:endposition]
                                print(f"AUTHORID THEN: {name}")
                                sample["author_id"] = name

                        else:
                            sample["followers"] = 0
                            sample["share_count"] = 0
                        frescsv.writerow(sample)
                    except ValueError:
                        print(file)
                        raise Exception


def csv_flattener(filename):
    def get_account_id(queryid):
        with open("/home/purusah/PycharmProjects/spidersRobin8/spider_facebook/input/KMCIC.csv",
                  "r") as f:
            csvq = csv.reader(f)
            for r in csvq:
                account_id = r[0]
                query = r[1]
                category_name = r[2]
                kwd = r[3]

                if query == queryid:
                    return account_id, category_name, kwd

    with open("flatten.csv", "w") as fw:
        csvwriter = csv.DictWriter(fw, fieldnames=config.fieldnames_output)
        csvwriter.writeheader()

        with open(filename, "r") as f:
            csvreader = csv.DictReader(f)
            next(csvreader, None)
            for row in csvreader:
                r = dict(row)
                if r.get("post_type") != "comment" and r.get("category_id"):
                    categories = eval(r.get("category_id"))
                    for category in categories:
                        rout = dict(r)
                        account_id, category_name, kwd = get_account_id(category)
                        rout.update({"category_id": category, "account_id": account_id, "category_name": category_name, "keywords": kwd})
                        print(f"CATEGORIES: {category} {r.get('post_type')}")
                        print(rout)
                        del rout["_id"]
                        del rout["iso_href"]
                        del rout["marked"]
                        del rout["collected"]
                        csvwriter.writerow(rout)
                else:
                    rout = dict(r)
                    rout.update({"category_id": "", "account_id": "", "keywords": ""})
                    del rout["_id"]
                    del rout["iso_href"]
                    del rout["marked"]
                    del rout["collected"]
                    csvwriter.writerow(rout)


if __name__ == "__main__":
    csv_compressor()
