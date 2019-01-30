
"""
Oracle utils


"""

import csv
import cx_Oracle
import pandas as pd


class OracleUtils:

    @staticmethod
    def convert_sequence_to_dict(lst):
        """for  cx_Oracle:
            For each element in the sequence, creates a dictionary item equal
            to the element and keyed by the position of the item in the list.
        """

        result = {}
        args = range(1, len(lst) + 1)

        for k, v in zip(args, lst):
            result[str(k)] = v

        return result

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = cx_Oracle.connect(self.connection_string)

    def table_exists(self, table_name):
        sql = "SELECT table_name FROM user_tables WHERE table_name = :table_name"

        cursor = self.connection.cursor()

        try:
            result = cursor.execute(sql, {'table_name': table_name.upper()})
            rows = result.fetchmany(1)

            return len(rows) > 0
        finally:
            cursor.close()

    def execute_statement(self, stmt, params=None):
        """
        Execute statement without returning result (delete, insert, update)
        :param params: parameters
        :param stmt: statement to execute
        """

        if params is None:
            params = {}

        cursor = self.connection.cursor()

        try:
            cursor.execute(stmt, params)
        finally:
            cursor.close()

    def execute_scalar(self, stmt):
        """
        Executes statement and returns first scalar value
        :param stmt: statement to select
        :return: first scalar value
        """

        cursor = self.connection.cursor()

        try:
            result = cursor.execute(stmt)
            rows = result.fetchmany(1)

            return rows[0][0]
        finally:
            cursor.close()

    def commit(self):
        """
        Commits transaction
        :return: None
        """

        self.connection.commit()

    def bulk_insert(self, stmt, df):
        """
        Bulk insert from Pandas DataFrame
        :param stmt: insert statement
        :param df: dataframe
        :return: None
        """

        cursor = self.connection.cursor()

        try:
            cursor.prepare(stmt)
            data = [OracleUtils.convert_sequence_to_dict(rec) for rec in df.values]
            cursor.executemany(None, data)
        finally:
            cursor.close()

    def load_to_csv(self, stmt, file_name, csv_delimiter, limit=10000):

        cursor = self.connection.cursor()

        try:
            cursor.execute(stmt)

            write_mode = 'w'
            write_header = True

            column_names = [col[0] for col in cursor.description]

            while True:
                rows = cursor.fetchmany(limit)
                if len(rows) == 0:
                    break

                df = pd.DataFrame(rows)
                df.columns = column_names
                df.to_csv(file_name, csv_delimiter, mode=write_mode, header=write_header, index=False,
                          quoting=csv.QUOTE_NONNUMERIC)

                if write_mode == 'w':
                    write_mode = 'a'
                    write_header = False

        finally:
            cursor.close()
