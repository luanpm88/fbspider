import csv
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

import config


def url_concat(url, args):

    if args is None:
        return url
    parsed_url = urlparse(url)
    if isinstance(args, dict):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args.items())
    elif isinstance(args, list) or isinstance(args, tuple):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args)
    else:
        err = "'args' parameter should be dict, list or tuple. Not {0}".format(
            type(args))
        raise TypeError(err)
    final_query = urlencode(parsed_query)
    url = urlunparse((
        parsed_url[0],
        parsed_url[1],
        parsed_url[2],
        parsed_url[3],
        final_query,
        parsed_url[5]))
    return url


def write_error(fname, data, reason=None, raise_exception=None):
    with open(fname, "w", encoding="utf-8") as f:
        f.write(data)


def uploadt_csv_toDB():
    db = config.dbr
    with open("input/KMCIC.csv") as f:
        csvreader = csv.reader(f)
        for i in csvreader:
            account_id = i[0]
            query_id = i[1]
            folder_name = i[2]
            keywords = i[3].split(",")
            # keywords = list(set([k for j in i[3].split(",") for k in j.split(" ")]))
            try:
                ind = keywords.index("")
                del keywords[ind]
            except ValueError:
                pass
            excluded = list(set([k for j in i[4].split(",") for k in j.split(" ")]))

            try:
                ind = excluded.index("")
                del excluded[ind]
            except ValueError:
                pass
            db["KMCIC"]["keywords"].insert_one(
                dict(
                    account_id=account_id,
                    query_id=query_id,
                    folder_name=folder_name,
                    keywords=keywords,
                    excluded=excluded
                )
            )
            print(f"{account_id} {query_id} {folder_name} {keywords} {excluded}")
    # with open("input/account_queries.csv") as f:
    #     cache = []
    #     csvreader = csv.reader(f)
    #     for i in csvreader:
    #         fb_link = i[0]
    #         ig_link = i[1]
    #         query_id = i[2]
    #
    #         if fb_link in cache:
    #             continue
    #         resp = db["KMCIC"]["accounts"].insert_one(
    #             {"query_id": query_id,
    #             "fb_link": fb_link[1:], "ig_link": ig_link[1:]}
    #         )
    #         cache.append(fb_link)
    #         # print(resp.raw_result)
    #         print(f"{fb_link} {ig_link} {query_id}")
    #         # raise Exception


if __name__ == "__main__":
    uploadt_csv_toDB()

