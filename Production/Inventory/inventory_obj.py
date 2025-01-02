import pandas as pd
import json
from datetime import datetime


LOW_STOCK_INFO_PATH = 'Production/Inventory/data/ls.json'
PREVIOUS_INV_INFO = 'Production/Inventory/data/prev_his.json'
INVENTORY_HISTORY_PATH = 'Production/Inventory/data/inv_his.json' 
ENCODING = 'utf-8'


class GrainVariety:
    '''Object to store total values of an active grain variety'''
    def __init__(self, variety:str) -> None:
        self.type:str = ''
        self.variety = variety
        self.get_type_variety()
        self.org_totes:int = 0 
        self.org_weight:int = 0 
        self.non_organic_totes = 0
        self.non_organic_weight = 0 
        self.seed_stock_totes:int = 0 
        self.seed_stock_weight:int = 0 
        self.total_weight:int = 0

    def __repr__(self):
        return f'<GrainVariety> "{self.type}, {self.variety}"'


    def get_type_variety(self):
        separated = self.variety.split(',')
        if len(separated) == 2:
            self.type = separated[0].strip()
            self.variety = separated[1].strip()
        elif len(separated) == 3 and separated[1].strip() == 'AP':
            self.type = 'Wheat'
        elif len(separated) == 3:
            self.type = separated[0].strip()
            self.variety = f'{separated[1].strip()}, {separated[2].strip()}'
        else:
            self.type = self.variety


class WarehouseGrainInventory:
    '''Object to store total values of all GrainVarieties in warehouse'''
    def __init__(self, data:pd.DataFrame) -> None:
        self.time:datetime = datetime.now().date()
        self.data = data
        self.varieties:list[str] = self.get_all_variety_names()
        self.working_varieties:list[str] = self.get_working_variety_names()
        self.total_inventory:list[GrainVariety] = self.get_all_inventory()
        self.ls_info:dict = self.load_ls_info()
        self.ls_varieties:list[GrainVariety] = self.check_low_stock()
        self.total_weight = self.get_total_weight()
        self.prev_history:dict = self.load_previous_json()
        self.total_inv_history:list[dict] = self.load_history_json() 
    

    def get_total_weight(self) -> int:
        tw = 0
        for item in self.total_inventory:
            tw += item.total_weight
        return tw


    def get_all_variety_names(self) -> list[str]:
        '''Get list of current varieties'''
        varieties_list = []
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] != 'Killed':
                if r['Variety'] not in varieties_list:
                    varieties_list.append(r['Variety'])
        return varieties_list
    

    def get_working_variety_names(self) -> list[str]:
        '''Get list of current working varieties'''
        varieties_list = []
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] == 'Working':
                if r['Variety'] not in varieties_list:
                    varieties_list.append(r['Variety'])
        return varieties_list


    def get_all_inventory(self) -> list[GrainVariety]:
        '''Creat list of GrainVariety objects to store current data'''
        varieties = [GrainVariety(item) for item in self.varieties]
        # Loop through inventory and add weights and number of totes to list of GrainVariety objects
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] != 'Killed':
                for obj in varieties:
                    if obj.variety == r['Variety'] or f'{obj.type}, {obj.variety}' == r['Variety']:
                        if not pd.isnull(r['Current Weight']):
                            obj.total_weight += int(r['Current Weight'])
                            if r['Organic Status'] != 'ORGANIC':
                                obj.non_organic_totes += 1
                                obj.non_organic_weight += int(r['Current Weight'])
                            elif r['Inventory Status'] == 'Seed Stock': 
                                obj.seed_stock_totes += 1
                                obj.seed_stock_weight += int(r['Current Weight'])
                            else:
                                obj.org_totes += 1
                                obj.org_weight += int(r['Current Weight'])
        return varieties
    

    def set_low_stock_console(self):
        '''Set low stock levels to check against current stocks. Save to JSON'''
        info = {}
        for item in self.working_varieties:
            print(item)
            low_stock = int(input('Enter number of totes to be considered Low Stock:\n'))
            info.update({item:low_stock})
        with open(LOW_STOCK_INFO_PATH, 'w', encoding=ENCODING) as file:
            json.dump(info, file, indent=4)
    

    def load_ls_info(self) -> dict | None:
        '''Load Low Stock Info'''
        try:
            with open(LOW_STOCK_INFO_PATH, 'r', encoding=ENCODING) as file:
                info = json.load(file)
            return info
        except FileNotFoundError:
            print('Low Stock Info - File not found.')
            return None
        

    def check_low_stock(self) -> list[GrainVariety]: 
        '''Checks for low stock, and adds GrainVariety objects to self.ls_varieties'''
        low_stock_list = []
        for item in self.total_inventory:
            for key in self.ls_info:
                if item.variety in key:
                    if item.org_totes <= self.ls_info[key]:
                        low_stock_list.append(item)
        return low_stock_list


    def save_prev_to_json(self):
        temp_dict_list = [item.__dict__ for item in self.total_inventory]
        dict_to_save = {
            f'{self.time}': temp_dict_list
        }
        with open(PREVIOUS_INV_INFO, 'w', encoding=ENCODING) as file:
            json.dump(dict_to_save, file, indent=4)


    def load_previous_json(self) -> dict:
        history = {}
        try:
            with open(PREVIOUS_INV_INFO, 'r', encoding=ENCODING) as file:
                history = json.load(file)
        except FileNotFoundError:
            print('Previous Inventory History - File not found')
        return history

############################### Saves List of All Previous Inventories ############################

    def save_history_to_json(self):
        temp_dict_list = [item.__dict__ for item in self.total_inventory]
        dict_to_save = {
            f'{self.time}': temp_dict_list
        }
        self.total_inv_history.append(dict_to_save)
        with open(INVENTORY_HISTORY_PATH, 'w', encoding=ENCODING) as file:
            json.dump(self.total_inv_history, file, indent=4)
        

    def load_history_json(self) -> list[dict]:
        history = []
        try:
            with open(INVENTORY_HISTORY_PATH, 'r', encoding=ENCODING) as file:
                history = json.load(file)
        except FileNotFoundError:
            print('Total Inventory History - File not found')
        return history
  




        

