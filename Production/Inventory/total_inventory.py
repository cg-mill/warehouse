import pandas as pd
from datetime import datetime, date
import json
from pathlib import Path


INDEX_FILEPATH = Path.joinpath(Path.cwd(), 'Production/Inventory/data/variety_index.json')
ENCODING = 'utf-8'


class Tote:
    def __init__(
            self,
            variety:str,
            grain_type:str = '',
            supplier:str = '',
            crop_id:str = '',
            date_received:datetime = datetime.now().date(),
            clean_date:datetime = '',
            kill_date:datetime = '',
            tote_num:int = 0,
            moisture:float = 0.0,
            protein:float = 0.0,
            weight:int = 0,
            cog:float = 0.0,
            receiving_notes:str = '',
            inv_notes:str = '',
            is_org:bool = True,
            is_killed:bool = False,
            is_clean:bool = False
            ) -> None:
        
        self.variety = variety
        self.grain_type:str = grain_type
        if self.grain_type == '':
            self.get_type_variety()
        self.supplier = supplier
        self.crop_id = crop_id
        self.date_received = date_received
        self.clean_date = clean_date
        self.kill_date = kill_date
        self.tote_num = tote_num
        self.moisture = moisture
        self.protein = protein
        self.weight = weight
        self.cog = cog
        self.value = self.get_value()
        self.receiving_notes = receiving_notes
        self.inv_notes = inv_notes
        self.is_org = is_org
        self.is_killed = is_killed
        self.is_clean = is_clean

    
    def get_value(self):
        if self.weight:
            return self.weight * self.cog


    def get_type_variety(self):
        separated = self.variety.split(',')
        if len(separated) == 2 and separated[0] != 'Barley':
            self.type = separated[0].strip()
            self.variety = separated[1].strip()
        elif separated[0] == 'Barley':
            self.type = separated[0].strip()
            self.variety = f'{separated[0].strip()}, {separated[1].strip()}'
        elif len(separated) == 3 and separated[1].strip() == 'AP':
            self.type = 'Wheat'
        elif len(separated) == 3:
            self.type = separated[0].strip()
            self.variety = f'{separated[1].strip()}, {separated[2].strip()}'
        else:
            self.type = self.variety

    
    def write_type_var(self):
        if self.grain_type == self.variety:
            return self.variety
        else:
            return f'{self.grain_type}, {self.variety}'
        

class Crop:
    def __init__(
            self,
            grain_type:str = '',
            variety:str = '',
            supplier:str = '',
            crop_id:str = '',
            date_received:datetime = datetime.now(),
            crop_year:str = '',
            moisture:float = 0,
            protein:float = 0,
            cog:float = 0,
            is_org:bool = True,
            is_clean:bool = False,
            receiving_notes:str = '',
            inventory_notes:str = '',
            total_weight:int = 0
            ) -> None:
        
        self.grain_type = grain_type
        self.variety = variety
        self.crop_index = self.get_index()
        self.supplier = supplier
        self.crop_id = crop_id
        self.date_received = date_received
        if crop_year != '':
            self.crop_year = str(crop_year) 
        elif crop_year == '' and isinstance(self.date_received, (datetime, date)):
            self.crop_year = str(self.date_received.year)
        else:
            self.crop_year = str(self.date_received)
        self.moisture = moisture
        self.protein = protein
        self.cog = cog
        self.is_org = is_org
        self.is_clean = is_clean
        self.receiving_notes = receiving_notes
        self.inventory_notes = inventory_notes
        self.totes:list[Tote] = []
        self.total_weight:int = total_weight
        self.total_value:float = 0


    def get_total_value(self):
        return self.total_weight * self.cog


    def get_index(self) -> int: 
        try:
            with open(INDEX_FILEPATH, 'r', encoding=ENCODING) as file:
                all_indexes = json.load(file)
            for variety in all_indexes:
                if variety == self.variety:
                    return all_indexes[variety]
        except FileNotFoundError:
            print('No Index File Found')


    def generate_crop_id(self, all_ids:list[str]) -> str:
        '''Generate a unique crop id when given all previously used crop ids'''
        add_on_chars = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        fp_string = self.supplier.strip().replace(' ', '').upper()[:3]
        sp_string = self.variety.strip().replace(' ', '').upper()[:3]
        base_string = fp_string + sp_string + self.crop_year[2:]
        if base_string not in all_ids:
            return base_string
        else:
            i = 1
            while i < 4:
                for char in add_on_chars:
                    id_string = base_string + char * i
                    if id_string not in all_ids:
                        return id_string
                i += 1
        

    def generate_tote_nums(self, all_previous_nums:list[int], num_to_generate:int) -> list[int]:
        '''Generate tote numbers for <num_to_generate> number of totes without 
        using any numbers from <all_previous_nums>'''
        num_to_start = int(f'{str(self.date_received.year)[2:]}{self.crop_index}001')
        while num_to_start in all_previous_nums:
            num_to_start += 1
        return [num for num in range(num_to_start, num_to_start+num_to_generate)]
    

    def create_totes(self, tote_nums:list[int]) -> list[Tote]:
        '''Creates a list of Tote objects with tote numbers being passed as arugument'''
        tote_weight = self.total_weight // len(tote_nums)
        totes = []
        for num in tote_nums:
            tote = Tote(
                variety=self.variety, 
                grain_type=self.grain_type,
                supplier=self.supplier,
                crop_id=self.crop_id,
                date_received=self.date_received,
                tote_num=num,
                moisture=self.moisture,
                protein=self.protein,
                weight=tote_weight,
                cog=self.cog,
                receiving_notes=self.receiving_notes,
                inv_notes=self.inventory_notes,
                is_org=self.is_org,
                is_clean=self.is_clean
                )
            totes.append(tote)
        return totes


class TotalInventory:
    def __init__(self, data:pd.DataFrame) -> None:
        self.data = data
        if type(self.data) == pd.DataFrame:
            self.variety_indexes = self.load_indexes()
            self.all_totes:list[Tote] = [self.get_tote(row[1]) for row in self.data.iterrows()]
            self.all_crops:list[Crop] = self.get_all_crops()
            self.total_weight:int = self.get_total_weight()
            self.total_value:float = self.get_total_value()
            # self.all_varieties:list[str] = self.get_all_varieties()

        
    def get_total_weight(self):
        tw = 0
        for tote in self.all_totes:
            if not tote.is_killed:
                tw += tote.weight
        return tw
    

    def get_total_value(self):
        tv = 0.0
        for tote in self.all_totes:
            if not tote.is_killed:
                tv += tote.value
        return tv
    
    
    def get_all_tote_nums(self) -> list[int]:
        '''Returns list of all tote numbers <int>, including killed'''
        return [tote.tote_num for tote in self.all_totes]
    

    def get_all_crop_id(self) -> list[str]:
        '''Returns list of all crop IDs, including killed'''
        crop_ids = []
        for tote in self.all_totes:
            if tote.crop_id not in crop_ids:
                crop_ids.append(tote.crop_id)
        return crop_ids


    def get_all_crops(self) -> list[Crop]:
        '''Retuns list of all ACTIVE Crop objects'''
        crop_ids = []
        crops:list[Crop] = []
        for tote in self.all_totes:
            if not tote.is_killed:
                if tote.crop_id not in crop_ids:
                    crop_ids.append(tote.crop_id)
                    crop = Crop(
                        grain_type=tote.grain_type,
                        variety=tote.variety,
                        supplier=tote.supplier,
                        crop_id=tote.crop_id,
                        date_received=tote.date_received,
                        moisture=tote.moisture,
                        protein=tote.protein,
                        cog=tote.cog,
                        is_org=tote.is_org,
                        inventory_notes=tote.inv_notes
                    )
                    crop.totes.append(tote)
                    crops.append(crop)
                else:
                    for crop in crops:
                        if tote.crop_id == crop.crop_id:
                            crop.totes.append(tote)
        for crop in crops:
            for tote in crop.totes:
                crop.total_weight += tote.weight
            crop.total_value = crop.total_weight * crop.cog
        return crops


    def get_tote(self, row) -> Tote:
        '''Converts pandas row to Tote object'''
        # if pd.isnull(row['Date Received']):
        #     row['Date Received'] = ''
        try:
            receiving_date = datetime.strptime(row['Date Received'], '%m/%d/%y')
        except (TypeError, ValueError):
            receiving_date = row['Date Received']

        try:
            date_cleaned = datetime.strptime(row['Clean Date'], '%m/%d/%y')
        except (TypeError, ValueError):
            date_cleaned = row['Clean Date']

        try:
            date_killed = datetime.strptime(row['Kill Date'], '%m/%d/%y')
        except (TypeError, ValueError):
            date_killed = row["Kill Date"]

        if pd.isnull(row['COGs']):
            row['COGs'] = 0

        tote = Tote(
            variety = row['Variety'],
            supplier = row['Farmer'],
            crop_id = row['Crop ID#'],
            date_received = receiving_date,
            clean_date = date_cleaned,
            tote_num = row['Tote #'],
            moisture = row['Moisture %'],
            protein = row['Protein %'],
            weight = row['Current Weight'],
            cog = row['COGs'],
            inv_notes = row['Notes']
        )
        if row['Organic Status'] != 'ORGANIC':
            tote.is_org = False
        if row['Inventory Status'] == 'Killed':
            tote.is_killed = True
        return tote


    def get_all_varieties(self) -> list[str]:
        varieties = []
        for tote in self.all_totes:
            if tote.variety not in varieties:
                varieties.append(tote.variety)
        return varieties
    

    def get_all_suppliers(self) -> list[str]:
        suppliers = []
        for tote in self.all_totes:
            if tote.supplier not in suppliers:
                suppliers.append(tote.supplier)
        return suppliers


    def set_indexes(self):
        index_dict = {}
        varieties = self.get_all_varieties()
        for var in varieties:
            print(var)
            index_num = input('Index Number:\n')
            index_dict.update({var:index_num})

        with open(INDEX_FILEPATH, 'w', encoding=ENCODING) as file:
            json.dump(index_dict, file, indent=4)


    def load_indexes(self) -> dict:
        try:
            with open(INDEX_FILEPATH, 'r', encoding=ENCODING) as file:
                 all_index = json.load(file)
                 return all_index
        except FileNotFoundError:
            print('Index File not Found')
            return {}
        
        

if __name__ == '__main__':
    import pandas as pd
    from total_inventory import TotalInventory

    INVENTORY_PATH = 'TESTING FILES/Warehouse Inventory.xlsm' # FOR HOME / TESTING

    data = pd.read_excel(
        INVENTORY_PATH, 
        index_col=False,
        sheet_name='All',
        usecols='A:N,P,Q',
        engine='openpyxl',
        # parse_dates=['Date Received','Clean Date']#,'MAP Date', 'Kill Date']
        )
    data.dropna(subset=['Tote #'], inplace=True)

    ti = TotalInventory(data=data)

    crop = Crop(
        variety="Ryman", 
        supplier="Vogler",
        date_received=datetime.now().date(),
        # crop_year=2024
        )
    crop.crop_id = crop.generate_crop_id(ti.get_all_crop_id())
    nums = crop.generate_tote_nums(all_previous_nums=ti.get_all_tote_nums(), num_to_generate=6)
    crop.totes = crop.create_totes(nums)
    for tote in crop.totes:
        print(tote.crop_id, tote.variety, tote.grain_type, tote.tote_num, tote.date_received)
        



