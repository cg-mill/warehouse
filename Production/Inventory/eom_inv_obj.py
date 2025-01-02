import os
import pandas as pd
import json
from datetime import datetime, timedelta
# import xlsxwriter as xl
# from decimal import * #TODO read docs, implement

# from inventory_obj import GrainVariety,WarehouseGrainInventory

ENCODING = 'utf-8'
PREV_HIST_PATH = 'Production/Inventory/data/eom/prev_his.json'
ALL_HIST_PATH = 'Production/Inventory/data/eom/total_history.json'
EXCEL_SAVE_TO_PATH = f"{os.environ['USERPROFILE']}/Team BSM Dropbox/Warehouse/EOM Inventory Totals + COGs"


class EOMGrainVariety:
    def __init__(self, variety:str, cog:float) -> None:
        self.variety = variety
        self.cog = cog
        self.total_weight:int = 0 
        self.total_value:float = None

    def get_total_value(self):
        self.total_value = self.total_weight * self.cog


#TODO changes from previous? 
#TODO mailer
class EOMWarehouseInventory:
    def __init__(self, data: pd.DataFrame) -> None:
        self.eom_time:datetime = self.get_eom_date()
        self.data = data
        self.varieties:list[tuple] = self.get_all_cogs_varieties()
        self.all_inventory:list[EOMGrainVariety] = self.get_all_inventory()
        self.total_weight:int = self.get_total_weight()
        self.total_inv_value:float = self.get_total_value()
        self.prev_history:dict = self.load_prev_json()
        self.all_history:list[dict] = self.load_history_json()

    
    def get_eom_date(self) -> datetime:
        current_date = datetime.now().date()
        next_date = current_date + timedelta(days=1)
        if next_date.month != current_date.month:
            return current_date
        else: 
            return current_date - timedelta(days=current_date.day)
        

    def get_all_cogs_varieties(self) -> list[tuple]:
        '''Get list of all varieties with associated COG as a tuple'''
        varieties_list = []
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] != 'Killed':
                if pd.isnull(r['COGs']):
                    r['COGs'] = 0
                var_cog = (r['Variety'], float(r['COGs']))
                if var_cog[1] == None:
                    var_cog[1] = 0
                if var_cog not in varieties_list:
                    varieties_list.append(var_cog)
        # print(varieties_list)
        return varieties_list


    def get_all_inventory(self) -> list[EOMGrainVariety]:
        varieties = [EOMGrainVariety(variety=item[0], cog=item[1]) for item in self.varieties]
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] != 'Killed':
                for var in varieties:
                    if var.variety == r['Variety'] and var.cog == float(r['COGs']):
                        var.total_weight += int(r['Current Weight'])
        for var in varieties:
            var.get_total_value()
        return varieties
    

    def get_total_weight(self) -> int:
        tw = 0
        for item in self.all_inventory:
            tw += item.total_weight
        return tw


    def get_total_value(self) -> float:
        tv = 0
        for item in self.all_inventory:
            tv += item.total_value
        return tv
    

    def save_to_xlsx(self):
        file_name = f'{self.eom_time} EOM Inventory.xlsx'
        full_file_path = f'{EXCEL_SAVE_TO_PATH}/{self.eom_time.year}/{file_name}'
        sheet_name = f'Inventory {self.eom_time}'
        info_dict = {
            'Variety': [var.variety for var in self.all_inventory],
            'Weight, lbs': [var.total_weight for var in self.all_inventory],
            'Price/lb (COG)': [var.cog for var in self.all_inventory],
            'Variety Total Value': [var.total_value for var in self.all_inventory],
        }
        df = pd.DataFrame(info_dict)
        df.loc[len(df)] = pd.Series()
        df.loc[len(df.index)] = ['Totals', self.total_weight, 'lbs', self.total_inv_value]
        
        with pd.ExcelWriter(full_file_path, mode='w', engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            bold_format = workbook.add_format()
            bold_format.set_bold()

            border = workbook.add_format({'border':1})
            
            cog_format = workbook.add_format({'num_format': '$#,##0.000'})
            dollar_format = workbook.add_format({'num_format': '$#,##0.00'})
            
            worksheet.write(0,0, f'Warehouse Inventory {self.eom_time}', bold_format)
            worksheet.set_column(0, 0, 35)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15, cog_format)
            worksheet.set_column(3, 3, 20, dollar_format)
            worksheet.set_row(0, 25)
            worksheet.set_row(2, 25)
            
            
    def save_prev_json(self):
        temp_dict_list = [item.__dict__ for item in self.all_inventory]
        dict_to_save = {
            f'{self.eom_time}': temp_dict_list
        }
        with open(PREV_HIST_PATH, 'w', encoding=ENCODING) as file:
            json.dump(dict_to_save, file, indent=4)


    def load_prev_json(self) -> dict:
        history = {}
        try:
            with open(PREV_HIST_PATH, 'r', encoding=ENCODING) as file:
                history = json.load(file)
        except FileNotFoundError:
            print('EOM Previous History File not found')
        return history
    

    def save_to_history_json(self):
        temp_dict_list = [item.__dict__ for item in self.all_inventory]
        dict_to_save = {
            f'{self.eom_time}': temp_dict_list
        }
        self.all_history.append(dict_to_save)
        with open(ALL_HIST_PATH, 'w', encoding=ENCODING) as file:
            json.dump(self.all_history, file, indent=4)


    def load_history_json(self) -> list[dict]:
        history = []
        try:
            with open(ALL_HIST_PATH, 'r', encoding=ENCODING) as file:
                history = json.load(file)
        except FileNotFoundError:
            print('EOM Total History File not found')
        return history 
    

if __name__ == "__main__":
    
    INVENTORY_PATH = f"{os.environ['USERPROFILE']}/Team BSM Dropbox/Warehouse/Warehouse Inventory.xlsm" # FOR WORK

    data = pd.read_excel(
    INVENTORY_PATH, 
    index_col=False,
    sheet_name='All',
    usecols='A:N,P,Q',
    engine='openpyxl',
    # parse_dates=['Date Received','Clean Date']#,'MAP Date', 'Kill Date']
    )
    data.dropna(subset=['Tote #'], inplace=True)

    eom = EOMWarehouseInventory(data=data)

    eom.save_prev_json()
    eom.save_to_history_json()
    eom.save_to_xlsx()