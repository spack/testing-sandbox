import argparse
from contextlib import closing
import sqlite3
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Query pipelines database""")
    parser.add_argument('--db-path', type=str, default=None, help="""Absolute path to sqlite3 database
file to open for querying.""")
    args = parser.parse_args()

    if not args.db_path:
        print('Error: no db path provided')
        sys.exit(1)

    with closing(sqlite3.connect(args.db_path)) as db_connection:
        with closing(db_connection.cursor()) as db_cursor:
            # List all the pipelines
            pipeline_rows = db_cursor.execute("SELECT pipeline_id, link, pr_number, branch FROM pipelines").fetchall()
            print('Pipelines ({0}):'.format(len(pipeline_rows)))
            for (pid, link, prnum, branch) in pipeline_rows:
                print('    {0}: {1}/{2} ({3})'.format(pid, prnum, branch, link))

            # Report how many builds are in the database
            num_builds = db_cursor.execute("SELECT COUNT(*) FROM builds;").fetchall()
            print('{0} total builds in the database'.format(num_builds))

            # Report any full hashes built multiple times and the number of builds
            full_hash_rebuilds = db_cursor.execute("""
                SELECT
                    pkg_name,
                    full_hash,
                    COUNT(*) c
                FROM builds
                GROUP BY full_hash HAVING c > 1
                ORDER BY c DESC
            ;""").fetchall()
            print('Full hash rebuilds:')
            for pkg_name, full_hash, count in full_hash_rebuilds:
                print('    {0} / {1}: {2}'.format(pkg_name, full_hash, count))


            # Report total number of rebuilds for each PR
            pr_rebuilds = db_cursor.execute("""
                SELECT
                    pipelines.pr_number,
                    COUNT(*) c
                FROM builds
                INNER JOIN pipelines ON builds.pipeline_id == pipelines.pipeline_id
                WHERE pipelines.pr_number != 'None'
                GROUP BY pipelines.pr_number
                ORDER BY c DESC
            ;""").fetchall()
            print('PR Rebuilds:')
            for pr_num, pkg_name in pr_rebuilds:
                print('    {0} -> {1}'.format(pr_num, pkg_name))

