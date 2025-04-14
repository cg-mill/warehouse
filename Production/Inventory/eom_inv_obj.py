import os
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
# import xlsxwriter as xl
# from decimal import * #TODO read docs, implement

# from inventory_obj import GrainVariety,WarehouseGrainInventory

ENCODING = 'utf-8'
PREV_HIST_PATH = 'Production/Inventory/data/eom/prev_his.json'
ALL_HIST_PATH = 'Production/Inventory/data/eom/total_history.json'
# EXCEL_SAVE_TO_PATH = Path.home().joinpath('Team BSM Dropbox/Warehouse/EOM Inventory Totals + COGs')
EXCEL_SAVE_TO_PATH = Path('TESTING FILES')


class EOMGrainVariety:
    def __init__(self, variety:str, cog:float, is_org:bool) -> None:
        self.variety = variety
        self.cog = cog
        self.is_org = is_org
        self.crop_id_list = []
        self.total_weight:int = 0 
        self.total_value:float | None = None
        self.loss:int = 0


    def get_total_value(self) -> None:
        self.total_value = self.total_weight * self.cog


class EOMWarehouseInventory:
    def __init__(self, data: pd.DataFrame, loss_data: pd.DataFrame, time:datetime.date = None) -> None:
        if time:
            self.eom_time = time
        else:
            self.eom_time:datetime = self.get_eom_date()
        self.data = data
        self.loss_data = loss_data
        self.varieties:list[tuple] = self.get_all_cogs_varieties()
        self.all_inventory:list[EOMGrainVariety] = self.get_all_inventory()
        self.total_weight:int = self.get_total_weight()
        self.total_inv_value:float = self.get_total_value()
        self.get_var_loss()
        self.add_org_variety_names()

    
    def get_eom_date(self) -> datetime:
        current_date = datetime.now().date()
        next_date = current_date + timedelta(days=1)
        if next_date.month != current_date.month:
            return current_date
        else: 
            return current_date - timedelta(days=current_date.day)
        

    def get_eom_dates(self) -> tuple[datetime]:
        current_date = datetime.now()
        previous_eom = current_date - timedelta(days=current_date.day)
        next_eom = current_date
        while next_eom.month == current_date.month:
            next_eom += timedelta(days=1)
        next_eom -= timedelta(days=1)
        return (previous_eom, next_eom)
    

    def choose_date_console(self):
        dates:tuple[datetime] = self.get_eom_dates()
        for i in range(len(dates)):
            print(f'{i}: {dates[i].date()}')
        answer = int(input('Please choose a number: '))
        return dates[answer]


    def get_all_cogs_varieties(self) -> list[tuple]:
        '''Get list of all varieties with associated COG as a tuple'''
        varieties_list = []
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] != 'Killed':
                if pd.isnull(r['COGs']):
                    r['COGs'] = 0
                org_status = True
                if r['Organic Status'] != 'ORGANIC':
                    org_status = False
                var_cog = (r['Variety'], float(r['COGs']), org_status)
                if var_cog[1] == None:
                    var_cog[1] = 0
                if var_cog not in varieties_list:
                    varieties_list.append(var_cog)
        # print(varieties_list)
        return varieties_list


    def get_all_inventory(self) -> list[EOMGrainVariety]:
        varieties = [EOMGrainVariety(variety=item[0], cog=item[1], is_org=item[2]) for item in self.varieties]
        for row in self.data.iterrows():
            r = row[1]
            if r['Inventory Status'] != 'Killed':
                org_status = True
                if r['Organic Status'] != 'ORGANIC':
                    org_status = False
                for var in varieties:
                    if (var.variety, var.cog, var.is_org) == (r['Variety'], r['COGs'], org_status):
                    # if var.variety == r['Variety'] and var.cog == float(r['COGs']):
                        var.total_weight += int(r['Current Weight'])
                        if r['Crop ID#'] not in var.crop_id_list:
                            var.crop_id_list.append(r['Crop ID#'])
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
    

    def add_org_variety_names(self) -> None:
        for var in self.all_inventory:
            if var.is_org:
                var.variety = f'ORG. {var.variety}'


    def get_var_loss(self) -> None:
        for row in self.loss_data.iterrows():
            r = row[1]
            for var in self.all_inventory:
                for crop in var.crop_id_list:
                    if r['Crop ID'] == crop and (r['Date Cleaning Finished'].month, r['Date Cleaning Finished'].year) == (self.eom_time.month, self.eom_time.year):
                        var.loss += r['Total Loss']
    

    def get_total_loss(self) -> tuple[int, float]:
        loss_weight = 0
        loss_value = 0.0
        for variety in self.all_inventory:
            loss_weight += variety.loss
            loss_value += variety.loss * variety.cog
        return (loss_weight, loss_value)


    def save_to_xlsx(self) -> None:
        file_name = f'{self.eom_time} EOM Inventory.xlsx'
        full_file_path = EXCEL_SAVE_TO_PATH.joinpath(str(self.eom_time.year), file_name)
        if full_file_path.parent not in full_file_path.parent.parent.iterdir():
            full_file_path.parent.mkdir(parents=True, exist_ok=True)
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
        
        loss_info_dict = {
            'Weight, lbs': [var.loss if var.loss > 0 else '' for var in self.all_inventory],
            'Price/lb (COG)': [var.cog if var.loss > 0 else '' for var in self.all_inventory],
            'Loss Total Cost': [var.loss * var.cog if var.loss > 0 else '' for var in self.all_inventory]
        }
        loss_df = pd.DataFrame(loss_info_dict)
        loss_df.loc[len(loss_df)] = pd.Series()
        loss_df.loc[len(df.index)] = [self.get_total_loss()[0], '', self.get_total_loss()[1]]

        with pd.ExcelWriter(full_file_path, mode='w', engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)
            loss_df.to_excel(writer, sheet_name=sheet_name, startrow=2, startcol=5, index=False)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            bold_format = workbook.add_format()
            bold_format.set_bold()

            border = workbook.add_format({'border': 1})
            top_border = workbook.add_format({'top': 1})
            
            cog_format = workbook.add_format({'num_format': '$#,##0.000'})
            dollar_format = workbook.add_format({'num_format': '$#,##0.00'})
            
            worksheet.write(0, 0, f'Warehouse Inventory {self.eom_time}', bold_format)
            worksheet.write(0, 5, 'Loss-Spillage Seed Cleaning & Receiving', bold_format)
            worksheet.set_column(0, 0, 35)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 15, cog_format)
            worksheet.set_column(3, 3, 20, dollar_format)
            worksheet.set_column(5, 5, 15)
            worksheet.set_column(6, 6, 15, cog_format)
            worksheet.set_column(7, 7, 20, dollar_format)
            for column in (0, 1, 2, 3, 5, 6, 7):
                worksheet.write(len(df)+1, column, '', top_border)
            worksheet.set_row(0, 25)
            worksheet.set_row(2, 25)
            
            
    def save_prev_json(self) -> None:
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
    

    def save_to_history_json(self) -> None:
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
    LOSS_LOG_PATH = Path.home().joinpath('Team BSM Dropbox/Food Safety/LOGS/Waste Log.xlsx')
    INVENTORY_PATH = Path.home().joinpath('Team BSM Dropbox/Warehouse/Warehouse Inventory.xlsm') # FOR WORK

    data = pd.read_excel(
        INVENTORY_PATH.as_posix(),
        index_col=False,
        sheet_name='All',
        usecols='A:N,P,Q',
        engine='openpyxl',
        # parse_dates=['Date Received','Clean Date']#,'MAP Date', 'Kill Date']
        )
    data.dropna(subset=['Tote #'], inplace=True)

    loss_data = pd.read_excel(
        LOSS_LOG_PATH.as_posix(),
        index_col=False,
        sheet_name='Receiving - Cleaning',
        usecols='C,H,L',
        engine='openpyxl',
        parse_dates=['Date Cleaning Finished']
    )
    loss_data.dropna(subset=['Crop ID'], inplace=True)

    eom = EOMWarehouseInventory(data=data, loss_data=loss_data)

    # eom.save_prev_json()
    # eom.save_to_history_json() 
    # eom.save_to_xlsx()
    eom.choose_date_console()