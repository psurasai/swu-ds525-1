#etl.py
from asyncio.windows_events import NULL
import glob
import json
import os
from typing import List

import psycopg2


table_insert_repo    = "INSERT INTO Repo VALUES %s ON CONFLICT DO NOTHING;"
table_insert_org     = "INSERT INTO Org VALUES %s ON CONFLICT DO NOTHING;"
table_insert_actor   = "INSERT INTO Actor VALUES %s ON CONFLICT DO NOTHING;"
table_insert_commit  = "INSERT INTO Commit VALUES %s ON CONFLICT DO NOTHING;"
table_insert_payload = "INSERT INTO Payload VALUES %s ON CONFLICT DO NOTHING;"
table_insert_event   = "INSERT INTO Event VALUES %s ON CONFLICT DO NOTHING;"


def get_files(filepath: str) -> List[str]:
    """
    Description: This function is responsible for listing the files in a directory
    """

    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, "*.json"))
        # files = glob.glob(os.path.join(root, "github_events.json"))
        for f in files:
            all_files.append(os.path.abspath(f))

    num_files = len(all_files)
    print(f"{num_files} files found in {filepath}")

    return all_files


def process(cur, conn, filepath):
    # Get list of files from filepath
    all_files = get_files(filepath)

    for datafile in all_files:
        with open(datafile, "r") as f:
            data = json.loads(f.read())
            for each in data:

                # Insert for Repo
                val = each["repo"]["id"], each["repo"]["name"], each["repo"]["url"]
                sql_insert = table_insert_repo % str(val)
                cur.execute(sql_insert)
                conn.commit()

                # Insert for Actor
                val = each["actor"]["id"], each["actor"]["login"], each["actor"]["display_login"], each["actor"]["gravatar_id"], each["actor"]["url"], each["actor"]["avatar_url"]
                sql_insert = table_insert_actor % str(val)
                cur.execute(sql_insert)
                conn.commit()

                # Insert for Org
                try:
                    val = each["org"]["id"], each["org"]["login"], each["org"]["gravatar_id"], each["org"]["url"], each["org"]["avatar_url"]
                    sql_insert = table_insert_org % str(val)
                    cur.execute(sql_insert)
                    conn.commit()
                except: pass

                # Insert for Commit
                try:
                    val = each["payload"]["commits"]["sha"], each["payload"]["commits"]["author"]["email"], each["payload"]["commits"]["author"]["name"], each["payload"]["commits"]["url"]
                    sql_insert = table_insert_commit % str(val)
                    cur.execute(sql_insert)
                    conn.commit()
                except: pass

                # Insert for Payload
                try:
                    val = each["payload"]["push_id"], each["payload"]["size"], each["payload"]["ref"], each["payload"]["commits"]["sha"]
                    sql_insert = table_insert_payload % str(val)
                    cur.execute(sql_insert)
                    conn.commit()
                except: pass

                # Insert for Event
                try: val = each["id"], each["type"], each["public"], each["created_at"], each["repo"]["id"], each["actor"]["id"], each["org"]["id"], each["payload"]["push_id"]
                except: 
                    try: val = each["id"], each["type"], each["public"], each["created_at"], each["repo"]["id"], each["actor"]["id"], each["org"]["id"], NULL
                    except: 
                        try: val = each["id"], each["type"], each["public"], each["created_at"], each["repo"]["id"], each["actor"]["id"], NULL, each["payload"]["push_id"]
                        except: val = each["id"], each["type"], each["public"], each["created_at"], each["repo"]["id"], each["actor"]["id"], NULL, NULL
                sql_insert = table_insert_event % str(val)
                cur.execute(sql_insert)
                conn.commit()


def main():
    conn = psycopg2.connect(
        "host=127.0.0.1 dbname=postgres user=postgres password=postgres"
    )
    cur = conn.cursor()

    process(cur, conn, filepath="../data/")

    conn.close()


if __name__ == "__main__":
    main()
