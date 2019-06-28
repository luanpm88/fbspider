
def update_db(self, results, es=False):

    for r in results:
        self.db["KMCIC"][self.collection].insert_one(r)
        if r["post_type"] != "comment" and es:
            post = esschema.Post(**r)
            post.meta.id = r.get("id")
            post.meta.index = self.index
            post.meta.doc_type = self.collection
            print(f"ADDED: {r}")

def export_db(self):
    with open("/output/{}", "w") as f:
        csvfile = csv.DictWriter(f, fieldnames=config.fieldnames_output)
        csvfile.writeheader()
        for r in self.db["KMCIC"][self.collection].find({}, {"_id": False}):
            if r.get("post_type") == "post":
                s = elasticsearch_dsl.Search(index="post") \
                    .query("match_phrase", post_data=r["post_data"]) \
                    .execute()
                for hit in s:
                    hit_id = s.get("id")
            csvfile.writerow(r)