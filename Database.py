# TODO: Merge all databases into one and have different tables for each subreddit

import sqlite3
import logging


class Database:
    # Subreddit Info Table
    TABLE_SUB_INFO = ""
    KEY1_USERNAME = "username"
    KEY1_RATELIMIT_START = "ratelimit_start"
    KEY1_RATELIMIT_COUNT = "ratelimit_count"
    KEY1_FLAIR_TEXT = "flair_text"
    KEY1_LAST_UPDATED = "last_updated"
    KEY1_FLAIR_PERM = "flair_perm"
    KEY1_CSS_PERM = "css_perm"
    KEY1_CUSTOM_FLAIR_USED = "custom_flair_used"
    KEY1_NO_AUTO_FLAIR = "no_auto_flair"

    # Subreddit Activity Table
    TABLE_SUB_ACTIVITY = "sub_activity"
    KEY2_USERNAME = "username"
    KEY2_SUB_NAME = "sub_name"
    KEY2_POSITIVE_POSTS = "positive_posts"
    KEY2_NEGATIVE_POSTS = "negative_posts"
    KEY2_POSITIVE_COMMENTS = "positive_comments"
    KEY2_NEGATIVE_COMMENTS = "negative_comments"
    KEY2_POSITIVE_QC = "positive_qc"
    KEY2_NEGATIVE_QC = "negative_qc"
    KEY2_POST_KARMA = "post_karma"
    KEY2_COMMENT_KARMA = "comment_karma"
    CREATE_SUB_ACTIVITY = ("CREATE TABLE IF NOT EXISTS " + TABLE_SUB_ACTIVITY + " (" +
                           KEY2_USERNAME + " TEXT, " + KEY2_SUB_NAME + " TEXT, " +
                           KEY2_POSITIVE_POSTS + " INTEGER, " + KEY2_NEGATIVE_POSTS + " INTEGER, " +
                           KEY2_POSITIVE_COMMENTS + " INTEGER, " + KEY2_NEGATIVE_COMMENTS + " INTEGER, " +
                           KEY2_POSITIVE_QC + " INTEGER, " + KEY2_NEGATIVE_QC + " INTEGER, " +
                           KEY2_POST_KARMA + " INTEGER, " + KEY2_COMMENT_KARMA + " INTEGER" +
                           ")")

    # Account Information Table
    TABLE_ACCNT_INFO = "accnt_info"
    KEY3_USERNAME = "username"
    KEY3_DATE_CREATED = "date_created"
    KEY3_POST_KARMA = "total_post_karma"
    KEY3_COMMENT_KARMA = "total_comment_karma"
    KEY3_LAST_SCRAPED = "last_scraped"
    CREATE_ACCNT_INFO = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_INFO + " (" +
                         KEY3_USERNAME + " TEXT PRIMARY KEY, " + KEY3_DATE_CREATED + " INTEGER, " +
                         KEY3_POST_KARMA + " INTEGER, " + KEY3_COMMENT_KARMA + " INTEGER, " +
                         KEY3_LAST_SCRAPED + " INTEGER" +
                         ")")

    # Create tables if needed
    def __init__(self, sub_name):
        # Connect to all tables
        self.conn = sqlite3.connect("master_databank.db", isolation_level=None, check_same_thread=False)
        cur = self.conn.cursor()

        # Create shared tables if necessary
        cur.execute(self.CREATE_SUB_ACTIVITY)
        cur.execute(self.CREATE_ACCNT_INFO)

        # Create subreddit table if necessary
        self.TABLE_SUB_INFO = sub_name
        cur.execute("CREATE TABLE IF NOT EXISTS " + self.TABLE_SUB_INFO + " (" +
                    self.KEY1_USERNAME + " TEXT PRIMARY KEY, " + self.KEY1_RATELIMIT_START + " INTEGER, " +
                    self.KEY1_RATELIMIT_COUNT + " INTEGER, " + self.KEY1_FLAIR_TEXT + " TEXT, " +
                    self.KEY1_LAST_UPDATED + " INTEGER, " + self.KEY1_FLAIR_PERM + " INTEGER, " +
                    self.KEY1_CSS_PERM + " INTEGER, " + self.KEY1_CUSTOM_FLAIR_USED + " INTEGER, " +
                    self.KEY1_NO_AUTO_FLAIR + " INTEGER"
                    ")")

        cur.close()

    # Check if a user exists in the account info table
    def exists_in_accnt_info(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY3_USERNAME + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY3_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        if data:
            return True
        else:
            return False

    def exists_in_sub_info(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY1_USERNAME + " FROM " + self.TABLE_SUB_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        if data:
            return True
        else:
            return False

    # Insert user data into Sub Info table
    def insert_sub_info(self, username, ratelimit_start, ratelimit_count, flair_txt, last_updated):
        # Set default permissions to False
        # These values are updated at different stages
        flair_perm = 0
        css_perm = 0
        custom_flair_used = 0
        no_auto_flair = 0

        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_SUB_INFO + "(" + self.KEY1_USERNAME + ", "
                      + self.KEY1_RATELIMIT_START + ", " + self.KEY1_RATELIMIT_COUNT + ", "
                      + self.KEY1_FLAIR_TEXT + ", " + self.KEY1_LAST_UPDATED + ", "
                      + self.KEY1_FLAIR_PERM + ", " + self.KEY1_CSS_PERM + ", "
                      + self.KEY1_CUSTOM_FLAIR_USED + ", " + self.KEY1_NO_AUTO_FLAIR
                      + ") "
                      + "VALUES(?,?,?,?,?,?,?,?,?)")

        cur.execute(insert_str, (username, ratelimit_start, ratelimit_count, flair_txt,
                                 last_updated, flair_perm, css_perm, custom_flair_used, no_auto_flair))
        cur.close()

    # Update existing user's data in Sub Info table
    def update_row_sub_info(self, username, ratelimit_start, ratelimit_count, flair_txt, last_updated):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_INFO
                      + " SET " + self.KEY1_RATELIMIT_START + " = ?, " + self.KEY1_RATELIMIT_COUNT + " = ?, "
                      + self.KEY1_FLAIR_TEXT + " = ?, " + self.KEY1_LAST_UPDATED + " = ? "
                      + "WHERE " + self.KEY1_USERNAME + " = ?")

        cur.execute(update_str, (ratelimit_start, ratelimit_count, flair_txt, last_updated, username))
        cur.close()

    # Insert user data into Account History table
    def insert_sub_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc,
                            sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts):
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_SUB_ACTIVITY + "("
                      + self.KEY2_USERNAME + ", " + self.KEY2_SUB_NAME + ", "
                      + self.KEY2_POSITIVE_POSTS + ", " + self.KEY2_NEGATIVE_POSTS + ", "
                      + self.KEY2_POSITIVE_COMMENTS + ", " + self.KEY2_NEGATIVE_COMMENTS + ", "
                      + self.KEY2_POSITIVE_QC + ", " + self.KEY2_NEGATIVE_QC + ", "
                      + self.KEY2_POST_KARMA + ", " + self.KEY2_COMMENT_KARMA + ") "
                      + "VALUES(?,?,?,?,?,?,?,?,?,?)")

        # Union of all keys in both primary dictionaries
        all_subs = sub_comment_karma.keys() | sub_post_karma.keys()
        # Put data from dictionaries into a list of tuples
        insert_data = [(username, sub, sub_pos_posts[sub], sub_neg_posts[sub], sub_pos_comments[sub],
                        sub_neg_comments[sub], sub_pos_qc[sub], sub_neg_qc[sub],
                        sub_post_karma[sub], sub_comment_karma[sub])
                       for sub in all_subs]
        cur.executemany(insert_str, insert_data)
        cur.close()
        logging.info("Sub activity inserted for " + username)

    # Update existing user's data in Account History table
    def update_sub_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc,
                            sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts):

        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_ACTIVITY + " SET "
                      + self.KEY2_COMMENT_KARMA + " = " + self.KEY2_COMMENT_KARMA + "+ ?, "
                      + self.KEY2_POSITIVE_COMMENTS + " = " + self.KEY2_POSITIVE_COMMENTS + "+ ?, "
                      + self.KEY2_NEGATIVE_COMMENTS + " = " + self.KEY2_NEGATIVE_COMMENTS + "+ ?, "
                      + self.KEY2_POSITIVE_QC + " = " + self.KEY2_POSITIVE_QC + "+ ?, "
                      + self.KEY2_NEGATIVE_QC + " = " + self.KEY2_NEGATIVE_QC + "+ ?, "
                      + self.KEY2_POST_KARMA + " = " + self.KEY2_POST_KARMA + "+ ?, "
                      + self.KEY2_POSITIVE_POSTS + " = " + self.KEY2_POSITIVE_POSTS + "+ ?, "
                      + self.KEY2_NEGATIVE_POSTS + " = " + self.KEY2_NEGATIVE_POSTS + "+ ? "
                      + "WHERE " + self.KEY2_USERNAME + " = ?")

        # Union of all keys in both primary dictionaries
        all_subs = sub_comment_karma.keys() | sub_post_karma.keys()
        for sub in all_subs:
            row_updated = cur.execute(update_str, (sub_comment_karma[sub], sub_pos_comments[sub], sub_neg_comments[sub],
                                                   sub_pos_qc[sub], sub_neg_qc[sub], sub_post_karma[sub],
                                                   sub_pos_posts[sub], sub_neg_posts[sub], username)).rowcount == 1
            if not row_updated:
                logging.debug("Row not updated - trying insert")
                insert_data = [{sub: item[sub]} for item in [sub_comment_karma, sub_pos_comments, sub_neg_comments,
                                                             sub_pos_qc, sub_neg_qc, sub_post_karma, sub_pos_posts,
                                                             sub_neg_posts]]
                self.insert_sub_activity(username, insert_data[0], insert_data[1], insert_data[2], insert_data[3],
                                         insert_data[4], insert_data[5], insert_data[6], insert_data[7])
                logging.debug("Successfully inserted data after failed update")
        cur.close()

    # Insert user data into Account Info table
    def insert_accnt_info(self, username, created, total_post_karma, total_comment_karma, last_scraped):
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_INFO + "("
                      + self.KEY3_USERNAME + ", " + self.KEY3_DATE_CREATED + ", "
                      + self.KEY3_POST_KARMA + ", " + self.KEY3_COMMENT_KARMA + ", "
                      + self.KEY3_LAST_SCRAPED + ") "
                      + "VALUES(?,?,?,?,?)")

        cur.execute(insert_str, (username, created, total_post_karma, total_comment_karma, last_scraped))
        cur.close()

    # Update user data in Account Info table
    def update_accnt_info(self, username, post_karma, comment_karma, last_scraped):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_INFO + " SET "
                      + self.KEY3_POST_KARMA + " = ?, " + self.KEY3_COMMENT_KARMA + " = ?, "
                      + self.KEY3_LAST_SCRAPED + " = ? "
                      + "WHERE " + self.KEY3_USERNAME + " = ?")

        cur.execute(update_str, (post_karma, comment_karma, last_scraped, username))
        cur.close()

    # Generic getter method for Account Info table
    def fetch_sub_info(self, username, key):
        select_key = self.find_key(key, self.TABLE_SUB_INFO)
        cur = self.conn.cursor()
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_SUB_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        value = data[0] if data is not None else None
        cur.close()
        return value

    # Generic getter method for Account History table
    def fetch_sub_activity(self, username, sub_list, key):
        select_key = self.find_key(key, self.TABLE_SUB_ACTIVITY)
        cur = self.conn.cursor()

        # Sum only the specified rows (subreddits)
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_SUB_ACTIVITY
                      + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                      + self.KEY2_SUB_NAME + " = ?")

        value = 0
        for name in sub_list:
            cur.execute(select_str, (username, name))
            data = cur.fetchone()
            if data is not None:
                value += data[0]
        return value

    def fetch_sub_activity_perc(self, username, sub_list, key):
        cur = self.conn.cursor()

        # Fix SUM() combining all users into one
        if key == "net qc":
            select_str = "SELECT rowid, " + self.KEY2_USERNAME + " FROM ( SELECT " \
                            "SUM(" + self.KEY2_POSITIVE_QC + ") - SUM(" + self.KEY2_NEGATIVE_QC + ") AS summed, " + \
                            self.KEY2_USERNAME + " FROM " + self.TABLE_SUB_ACTIVITY + \
                            " WHERE " + self.KEY2_SUB_NAME + " IN ('" + "', '".join(sub_list) + "')" \
                            " ORDER BY summed DESC " +  \
                         ") WHERE " + self.KEY2_USERNAME + " = ?"
        else:
            select_key = self.find_key(key, self.TABLE_SUB_ACTIVITY)

            select_str = "SELECT rowid FROM (" \
                            "SELECT SUM(" + select_key + ") AS summed " \
                            "FROM " + self.TABLE_SUB_ACTIVITY + \
                            " ORDER BY summed DESC" \
                            "WHERE " + self.KEY2_SUB_NAME + " IN (" + ", ".join(sub_list) + ")" \
                         ") WHERE " + self.KEY2_USERNAME + " = ?"

        cur.execute(select_str, (username,))
        test = cur.fetchone()[0]
        return test

    # Generic getter method for Account Info table
    def fetch_accnt_info(self, username, key):
        cur = self.conn.cursor()
        select_key = self.find_key(key, self.TABLE_ACCNT_INFO)
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY3_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value

    # Generic updater method for sub info table
    def update_key_sub_info(self, username, key, value):
        cur = self.conn.cursor()
        update_key = self.find_key(key, self.TABLE_SUB_INFO)

        update_str = ("UPDATE " + self.TABLE_SUB_INFO + " SET " + update_key + " = ? "
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        cur.execute(update_str, (value, username))
        cur.close()

    def wipe_sub_info(self):
        cur = self.conn.cursor()
        delete_str = "DELETE FROM " + self.TABLE_SUB_INFO
        cur.execute(delete_str)
        cur.close()

    # Turn string from INI file into a key
    def find_key(self, key, table):
        key = key.lower()
        if table == self.TABLE_SUB_INFO:
            if key == "ratelimit start":
                return self.KEY1_RATELIMIT_START
            elif key == "ratelimit count":
                return self.KEY1_RATELIMIT_COUNT
            elif key == "flair text":
                return self.KEY1_FLAIR_TEXT
            elif key == "last updated":
                return self.KEY1_LAST_UPDATED
            elif key == "flair perm":
                return self.KEY1_FLAIR_PERM
            elif key == "css perm":
                return self.KEY1_CSS_PERM
            elif key == "custom flair used":
                return self.KEY1_CUSTOM_FLAIR_USED
            elif key == "no auto flair":
                return self.KEY1_NO_AUTO_FLAIR

        elif table == self.TABLE_SUB_ACTIVITY:
            if key == "sub name":
                return self.KEY2_SUB_NAME
            if key == "positive posts":
                return self.KEY2_POSITIVE_POSTS
            if key == "negative posts":
                return self.KEY2_NEGATIVE_POSTS
            if key == "positive comments":
                return self.KEY2_POSITIVE_COMMENTS
            if key == "negative comments":
                return self.KEY2_NEGATIVE_COMMENTS
            if key == "positive qc":
                return self.KEY2_POSITIVE_QC
            if key == "negative qc":
                return self.KEY2_NEGATIVE_QC
            if key == "post karma":
                return self.KEY2_POST_KARMA
            if key == "comment karma":
                return self.KEY2_COMMENT_KARMA

        elif table == self.TABLE_ACCNT_INFO:
            if key == "date created":
                return self.KEY3_DATE_CREATED
            elif key == "total post karma":
                return self.KEY3_POST_KARMA
            elif key == "total comment karma":
                return self.KEY3_COMMENT_KARMA
            elif key == "last scraped":
                return self.KEY3_LAST_SCRAPED

        else:
            logging.warning("Could not find a match for key in the given table"
                            "\nKey: " + key + "\tTable:" + table)
            return None
