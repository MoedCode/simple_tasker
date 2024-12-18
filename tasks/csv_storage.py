

import csv
import os
from collections import Counter
from tasks.main import *
from typing import List, Dict
import inspect
from typing import Union, Dict, List
class XO:
    immutable = ["x", "o"]
class OX(XO):
    KEYS = ["O", "X", "x", "y", "Y"]
    pass
class CsvStorage():
    def __init__(self, file_name='output.csv', mode='a',line='', clm_names=[], pair_class=OX, inst_name=None) -> None:
        self.tasks_dir = os.path.dirname(__file__)  # Gets the directory of the current file (tasks)
        self.file_path = os.path.join(self.tasks_dir, file_name)  # Build the full path within tasks
        self.line = line
        self.mode = mode
        self.session  = []
        self.pair_class = pair_class
        self.clm_names = sorted(self.pair_class.KEYS)
        self.immutables = sorted(self.pair_class.immutable_instattr )
        self.inst_name =   inst_name or     pair_class.__name__.lower()
    def reader(self):
        try:
            file = open(self.file_path, mode='r')  # Open the file
            reader = csv.reader(file)  # Use the file
            return  file, reader
        except Exception as e:
            raise e
    def get_columns(self, columns_names: str = "", map:bool = False) -> List[str]:
        """
        Get one or more CSV columns by their names.
        Args:
            columns_names (str): The name(s) of the column(s) to retrieve
        Returns:
            List[str]: The values in the specified column(s).
        """
        if isinstance(columns_names, str):
            columns_names = [columns_names]

        file, reader = self.reader()
        header = next(reader)  # Read the header row
        try:
            idxs = [header.index(name) for name in columns_names]
        except ValueError as e:
            file.close()
            return [False, str(ValueError(f"Column '{columns_names}' not found in CSV file."))]

        data = {name: [] for name in columns_names}  # Initialize a dict for results
        rows = list(reader)  # Convert reader to a list to allow multiple passes
        if not map:
            file.close()
            result = [header[:]]  # Initialize the result list

            # Iterate over each column index in idxs
            for idx in idxs:
                # For each column index, collect the values from rows
                column_data = [
                    row[idx] if idx < len(row) and row[idx] else None  # Check index and handle empty values
                    for row in rows
                ]
                result.append(column_data)  # Append the column data to the result
            return result


        for idx, name in zip(idxs, columns_names):
            data[name] = [
                row[idx] if idx < len(row) and row[idx] else None  # Check index and handle empty values
                for row in rows
            ] # Collect column values
        data["header"] = header[:]
        file.close()
        return data

    def filter(self, query:dict={}, first=False) ->List[str]:
        """
        filters data by provided key value in dict
        Args:
        query (dict) : to filter data
        """
        value , key = "", ""
        key = list(query.keys())[0]; value = query[key]
        file, reader= self.reader()
        header = next(reader)
        idx = header.index(key)
        values_lists = []
        for row in reader:
            if row[idx] == value:
                values_lists += [row[:]]
                if first:
                    break
        if first:
            file.close()
            return dict(zip(header, values_lists[0]))
        map_dicts = []
        for values in values_lists:
            map_dicts.append( dict(zip(header, values)))
        file.close()
        return map_dicts
    def search(self, query_data: Dict = {}, caller=None) -> Union[List[Dict], Dict]:
        """
        search - Searches for rows in a dataset that match the given criteria.
        Args:
            query_data: (dict) includes:
                - method: (str) Search method ('startwith', 'include', 'identical').
                - query: (dict) Key-value pairs to filter rows by.
                - case_sensitive: (bool, optional) Whether to perform case-sensitive matching. Default is False.
        Returns:
            - List[Dict]: Matching rows as a list of dictionaries, if successful.
            - Dict: Error information, if an error occurs.
        """
        # Validate query_data
        if "Users.csv" in self.file_path or "Auth.csv" in self.file_path:
            if caller and (caller.__class__.__name__ == "Authentication" or caller.__name__ == "Authentication" ):
                pass
            else :

                return [False, {"Error":"mesh men hena "}]
        error_msg = ""
        if not query_data or not isinstance(query_data, dict):
            return {"Error": "Invalid query_data. Must be a dictionary."}

        query = query_data.get("query", {})
        method = query_data.get("method", "").lower()
        case_sensitive = query_data.get("case_sensitive", False)

        if not query:
            error_msg += "No query provided. "
        if not method:
            error_msg += "No method specified. "
        if method not in ("startwith", "include", "identical"):
            error_msg += f"Unsupported method '{method}'. Use 'startwith', 'include', or 'identical'. "

        if error_msg:
            return {"Error": error_msg.strip()}

        # Read all data from CSV
        file, reader = self.reader()
        header = next(reader)  # Get the header row
        rows = [dict(zip(header, row)) for row in reader]  # Convert rows to dictionaries
        file.close()

        # Filter rows based on query
        matches = []
        for row in rows:
            match = True
            for key, value in query.items():
                if key not in row:
                    match = False
                    break

                col_value = row[key] if case_sensitive else row[key].lower()
                value_to_match = value if case_sensitive else value.lower()

                if method == "startwith" and not col_value.startswith(value_to_match):
                    match = False
                elif method == "include" and value_to_match not in col_value:
                    match = False
                elif method == "identical" and col_value != value_to_match:
                    match = False

                if not match:
                    break

            if match:
                matches.append(row)

        return matches if matches else [False, {"Message": "No matching rows found."}]


    def search_old(self,  query_data:Dict = {}) -> Union[List[Dict], Dict]:
        """
        search - Searches for rows in a dataset that match the given criteria.
        Args:
        column_name: (str) The name of the column to search in. Defaults to an empty string.
        query_data: (dict) Key-value pairs to filter rows by. Supports nested dictionaries. Defaults to an empty dictionary.
        Return:
            - List[Dict]: A list of dictionaries representing matching rows, if successful.
            - Dict: A dictionary includeing error information, if an error occurs.
        """
        # handling potential issues
        error_msg = ""
        if not  query_data or not isinstance(query_data, dict): error_msg += "No data to filter,  "
        # get search method  search keys"column names"" and values
        query = query_data.get("query", {})
        method = query_data.get("method", "")
        keys , values = list(query.keys()) , list(query.values())
        if not  query_data["method"]: error_msg += "No valid method to filter, "
        if not  query : error_msg += "No valid query to filter, "
        if  not keys or not values:
            error_msg += f"query must be dict for key and values, keys:{keys} , values:{values} "
        if error_msg:
            return [False, {"Error":error_msg}]
        # query all column
        columns = self.get_columns(keys, True)

        if ("case_sens", "case_sensitive", ) in query_data:
            case_sens = query_data["case_sens"] or query_data["case_sensitive"]
        else: case_sens = False
        # get search keys
        # get columns crossponding to search values
        # header = columns.pop(0)
        result_dict = {}

        col_len = len(columns["header"])
        del columns["header"]
        for key, clm_values in columns.items():
            result_dict[key] = []
            for clm_value in clm_values:
                DEBUG(f"clm_value {clm_value },: {type(clm_value)}")
                if clm_value and clm_value.startswith(query[key]):
                    result_dict[key].append(clm_value)
        return result_dict
        if not case_sens :
            values = [value.lower() for value in values]
            columns = [[el.lower() for el in column] for column in  columns]
        if method in  ("start_with", "start with", "startwith"):
            matching_result = []
            # for value in
        # for i in range(len jeys)
    def write_line(self, query:dict={}, to_write:dict={}, W_PWD=False) -> str:
        """
            write Line in csv file
            Args:
            query (dict) : key value to get the concern line
            to_write (dict) : data to write the line
        """
        if not query or not to_write:
            return None
        key  = list(query.keys())[0]; value = query[key]
        file, reader= self.reader()
        header = next(reader); idx =  header.index(key)
        reader = list(reader)
        '''check if any key in to_write object not  exist in header
         or not exist but not accessible '''
        # remove password from not_accessible key if A
        immutables_copy = self.immutables[:]
        # Correctly access the stack and the filename of the caller
        if W_PWD:
            immutables_copy.remove("password")

        write_k, not_match, not_accessible ,   msg = list(to_write.keys()) , [], [], ""
        for element in write_k:
            if element not in header:
                not_match += [element[:]]
            if element in immutables_copy:
                not_accessible +=[element[:]]
        # confirming error objet
        if not_match :  msg = " {not_match keys: "+ ", ".join(not_match) + "}"
        if not_accessible: msg = " {not_accessible keys: "+ ", ".join(not_accessible) + "}"
        # return errors object if there are an errors
        if msg:
            file.close()
            return {"Error":msg}

        # replacing
        written_values = ""
        new_row = []
        for row in  reader:
            if row[idx] == value:
                new_row = row

                DEBUG(f"row[idx]=> {row[idx]}")
                for i in range(len(row) ):
                    if header[i] in write_k:
                        #skip if they are already the same
                        if row[i] == to_write[header[i]]:
                            continue
                        DEBUG(f"{i}")
                        row[i] = to_write[header[i]]
                        written_values += f"{header[i]}"
                        written_values += ":"
                        written_values += f"{row[i]}"
                        written_values += ", "
            if not written_values:
                file.close()
                return {"status":False, "message":"no any new value to update"}
        res = self.write_file(reader=reader, header=header)
        x = dict(zip(header, new_row))
        query = {} ; query[key] = x[key]
        return self.filter(query=query, first=True)
    def write_file(self, reader:List[List]=[], header:List=[]) -> bool:
        if not reader:
            return False
        if not header:
            header = self.clm_names
        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Write the header
            writer.writerows(reader)
        return True




    def csv_read(self):


        data_list = []  # List to store each row as a dictionary

        try:
            with open(self.file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)  # Automatically uses header as keys
                for row in csv_reader:
                    # Append each row as-is (as a dictionary) to the data_list
                    data_list.append(dict(row))

            # print("Data successfully read.")
            return data_list  # Return the list of dictionaries

        except FileNotFoundError:
            print(f"File {self.file_path} not found.")
            return [False,"File {self.file_path} not found."]
        except Exception as e:
            print(f"An error occurred: {e}")
            return [False, f"An error occurred: {e}"]
    def reload(self):
        self.session =  self.csv_read()
        # print(f"\n\n\n ------------   -------------- \n\n\n")
        return len(self.session)
    def add(self, data):
        if not data or type(data) != dict:
            return False, f"{type(data)} .."
        data_k = sorted(list(data.keys()))
        # not_match = [key for key in data.keys() if key not in Users.KEYS]

        not_match = [key for key in data.keys() if key not in self.clm_names]
        if Counter(data_k) != Counter(self.clm_names):
            return False, f" {not_match} not match  self.cllm {self.clm_names} "
        self.session.clear()
        self.reload()
        self.session.append(data)

        # print(f"\n\n from storage add :: \n{self.session}\n")
        print(f"\n\n\n {self.add.__name__} instname {self.inst_name}")
        # self.session = []
        return True, "data added successfully"
    def save(self):
        result = self.csv_write(self.session)
    def csv_write(self, data):

        # Build the path to save output.csv within the tasks directory

        try:
            # For debugging, print the absolute path where the file will be saved
            abs_path = os.path.abspath(self.file_path)
            print(f"Attempting to write to file at: {abs_path}")

            # Extract field names from the first dictionary in the data list
            fieldnames = self.clm_names

            with open(file=self.file_path, mode=self.mode, newline=self.line) as file:
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames)

                # Write header only if the file is being created or overwritten
                if self.mode == 'w':
                    csv_writer.writeheader()

                # Write the data rows
                csv_writer.writerows(data)
                # self.session.clear()
            print(f"\n\nData written successfully to {abs_path}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_by(self, key=None, value=None):
        # print(f"\n\n from csv_storage:get_by >> key {key} value {value}")
        if not key or not value:
            return False, f"\n{self.get_by.__name__}:\nmessing {'key' if key is None else ''} {'value' if value is None else ''} ."
        if key not in self.clm_names:
            return False, f"key {key} not match"
        self.reload()
        for idx, task in enumerate(self.session):
            # print(f"key : {key} value : {value}")

            if task[key] == value:
                return True, task, idx
        return False, f"{key} : {value} not found "
    def is_exist(self, key=None, value=None):
        result = self.get_by(key, value)
        if not result[0] and "messing" in result[1]:
            return result
        if result[0]:
            return "Exist" ,result[1],value
        if not result[0] and "not match" in result[1]:
            return "Not Exist", f"{key}:{value} not found"
        return False, f" unknown error {self}:: is_exist()"
    def update(self, key="", value=None, data={}):
        data_k = list(data.keys())
        # return False, data_k
        not_match = [key for key in data.keys() if key not in self.clm_names]
        if not_match:
            return False, f" {not_match} not match  self.cllm {self.clm_names} "
        Err = [key for key in data.keys() if key  in self.immutables]
        if Err:
            msg = ", ".join(Err)
            return False, f" cant update {msg} from here "
        query = self.get_by(key, value)
        if not query[0]:
            return False, query[1]
        idx = query[2]
        from datetime import datetime
        DEBUG(f"{self.file_path}")
        for key, value in data.items():
            self.session[idx][key] = value
        self.session[idx]["updated"] =  datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.save()
        return True, f" updated  "

    def delete(self, key=None, value=None):
        res = self.get_by(key=key, value=value)
        if not res[0]:
            return  res[0], res[1]

        self.session.pop(res[2])
        self.save()
        return True, f"{self.inst_name} deleted"
        # self.session = []
        # self.reload()
        # return True, f"{self}"

    def multi_selection(self, select_by=None, val_lst=[], action="get"):
        if not select_by or not len(val_lst) or select_by not in self.clm_names:
            msg = f"{' -empty list.' if not  len(val_lst) else '' }"
            msg += f"{'-No key to select by' if not  select_by else ''}"
            msg += f"-{select_by} Not A valid Key" if select_by not in self.clm_names else ""
            return False, msg
        self.reload()
        selected_tasks = []
        indexes = []
        for val in val_lst:
            for index, task in enumerate(self.session):
                if task[select_by] == val:
                    indexes.append(index)
                    selected_tasks.append(task)
        if not len(selected_tasks):
            return False, f"No Result Match {val_lst}"
        if action == "get":
            return True, selected_tasks, indexes
        if action == "delete":
            for index in indexes:
                self.session.pop(index)
                self.save()

