import customtkinter as ctk
import pandas as pd
from tkinter import messagebox
import json
from pathlib import Path
from datetime import datetime

from Inventory import GrainVariety, WarehouseGrainInventory, EOMWarehouseInventory

#TODO make Path objects and test
# INDEX_FILEPATH = 'Production/Inventory/data/variety_index.json'
# FONT_INFO_PATH = 'Production/Inventory/data/font_info.json'
LOW_STOCK_INFO_PATH = 'Production/Inventory/data/ls.json'
ENCODING = 'utf-8'

#TESTING PATHS
INDEX_FILEPATH = 'TESTING FILES/variety_index.json'
FONT_INFO_PATH = 'TESTING FILES/font_info.json'


def get_font_index_info() -> tuple[dict, dict]:
    '''Returns font info in idex[0], index info index[1]'''
    with open(INDEX_FILEPATH, 'r', encoding=ENCODING) as file:
        var_indexes:dict = json.load(file)
    with open(FONT_INFO_PATH, 'r', encoding=ENCODING) as file:
        font_info:dict = json.load(file)
    return (font_info, var_indexes)


class LowStockFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, data:pd.DataFrame, **kwargs):
        super().__init__(master, **kwargs)
        inv = WarehouseGrainInventory(data=data)
        if len(inv.ls_varieties) > 0:
            title_label = ctk.CTkLabel(master=self, text='Low Stock', font=ctk.CTkFont('sans serif', 50, 'bold'), text_color='red' )
            title_label.pack(pady=(10, 20))
            for item in inv.ls_varieties:
                var_frame = SingleVarietyFrame(self, item)
                var_frame.pack()


class LowStockEditSingle(ctk.CTkFrame):
    def __init__(self, master, info: tuple, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.label = ctk.CTkLabel(master=self, text=info[0], anchor='e')
        self.label.grid(row=0, column=0, sticky ='w', padx=5)
        self.value_input = ctk.CTkEntry(master=self, placeholder_text=info[1], width=50)
        self.value_input.grid(row=0, column=1, sticky='e', padx=5)


class LowStockEditFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, data: pd.DataFrame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.data = data
        self.master = master
        width = 250
        inv = WarehouseGrainInventory(data=data)
        current_levels = inv.load_ls_info()
        for item in inv.working_varieties:
            if item in current_levels:
                entry = LowStockEditSingle(master=self, info=(item, current_levels[item]), width=width)
            else:
                entry = LowStockEditSingle(master=self, info=(item, None), width=width)
            entry.pack(pady=5)

        self.submit_button = ctk.CTkButton(master=self,text='Submit', command=self.submit_call)
        self.submit_button.pack(pady=5)
        self.cancel_button = ctk.CTkButton(master=self, text='Cancel')            
        self.cancel_button.pack(pady=(5,30)) #TODO make success messsagebox instead of label. 
        self.success_label = ctk.CTkLabel(master=self, text='Saved', text_color='green')
    

    def submit_call(self):
        ls_data = {}
        for key in self.children:
            var = self.children[key]
            if isinstance(var, LowStockEditSingle):
                name = var.label.cget('text')
                if var.value_input.get():
                    try:
                        val = int(var.value_input.get())
                    except ValueError:
                        messagebox.showerror(title='Input Error', message='Please only input whole numbers!')
                        return     
                else:
                    val = var.value_input.cget('placeholder_text')
                ls_data.update({name:val})
        with open(LOW_STOCK_INFO_PATH, mode='w', encoding=ENCODING) as file:
            json.dump(ls_data, file, indent=4)
        # print(self.grid_info())
        # for item in self.pack_slaves():
        #     self.pack_forget()
        self.success_label.pack(pady=(0,20))



class QuickViewFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, data:pd.DataFrame, **kwargs):
        super().__init__(master, **kwargs)

        self.inventory = WarehouseGrainInventory(data=data)
        total_iterations = 0
        row = 0
        for item in self.inventory.total_inventory:
            if total_iterations % 2 != 0 and total_iterations != 1:
                row +=1
            var_frame = SingleVarietyFrame(self, item)
            var_frame.grid(row=row, column=total_iterations%2)
            total_iterations += 1


class SingleVarietyFrame(ctk.CTkFrame):
    def __init__(self, master, variety:GrainVariety, **kwargs):
        super().__init__(master, **kwargs)
        var_string = ''
        if variety.type == variety.variety:
            var_string = variety.type
        else:
            var_string = f'{variety.type}, {variety.variety}'
        self._border_width = 2
        self.variety_label = ctk.CTkLabel(self, text=var_string, anchor='w')
        self.variety_label.grid(row=0, column=0, columnspan=3, pady=(5, 0), padx=5, sticky='w')
        self.org_label = ctk.CTkLabel(self, text='Organic')
        self.org_label.grid(row=1, column=1, padx=5)
        self.non_org_label = ctk.CTkLabel(self, text='Non Organic')
        self.non_org_label.grid(row=1, column=2, padx=5)
        self.seed_stock_label = ctk.CTkLabel(self, text='Seed Stock')
        self.seed_stock_label.grid(row=1, column=3, padx=5)
        self.totes_label = ctk.CTkLabel(self, text='Totes')
        self.totes_label.grid(row=2, column=0, padx=5)
        self.weight_label = ctk.CTkLabel(self, text='Weight')
        self.weight_label.grid(row=3, column=0, padx=5, pady=(0,5))

        self.ot_value = ctk.CTkLabel(self, text=variety.org_totes)
        self.ot_value.grid(row=2, column=1)
        self.ow_value = ctk.CTkLabel(self, text=variety.org_weight)
        self.ow_value.grid(row=3, column=1, pady=(0,5))
        self.no_t_value = ctk.CTkLabel(self, text=variety.non_organic_totes)
        self.no_t_value.grid(row=2, column=2)
        self.no_w_value = ctk.CTkLabel(self, text=variety.non_organic_weight)
        self.no_w_value.grid(row=3, column=2, pady=(0,5))
        self.sst_value = ctk.CTkLabel(self, text=variety.seed_stock_totes)
        self.sst_value.grid(row=2, column=3)
        self.ssw_value = ctk.CTkLabel(self, text=variety.seed_stock_weight)
        self.ssw_value.grid(row=3, column=3, pady=(0,5))


class FontInfoFrame(ctk.CTkFrame):
    def __init__(self, master, key:str, item_name:str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        pass#TODO ? Necessary or not?


class NewVarietyWindow(ctk.CTkToplevel):
    def __init__(self, var_name:str, *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.geometry('350x350')
        self.title('Assign Variety Index and Font Info')
        self.view = NewVarietyFrame(master=self, var_name=var_name)
        self.view.pack()
        self.grab_set()
        

class NewVarietyFrame(ctk.CTkFrame):
    def __init__(self, master, var_name:str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        with open(INDEX_FILEPATH, 'r', encoding=ENCODING) as file:
            self.var_indexes:dict = json.load(file)
        with open(FONT_INFO_PATH, 'r', encoding=ENCODING) as file:
            self.font_info:dict = json.load(file)
        self.type_ranges = {
            'Wheat': [str(num)for num in range(67, 100) if str(num) not in self.var_indexes.values()],
            'Corn': [str(num) for num in range(21, 31) if str(num) not in self.var_indexes.values()],
            'Rye': [str(num) for num in range(31, 36) if str(num) not in self.var_indexes.values()],
            'Legumes': [str(num) for num in range(36, 41) if str(num) not in self.var_indexes.values()],
            'Ancient': [str(num) for num in range(41, 51) if str(num) not in self.var_indexes.values()],
            'Rice': [str(num) for num in range(51, 56) if str(num) not in self.var_indexes.values()],
            "Buckwheat": [str(num) for num in range(56, 61) if str(num) not in self.var_indexes.values()]
        }
        self.g_type_options = ctk.CTkOptionMenu(self, values=[key for key in self.type_ranges], command=self.g_type_options_callback)
        self.g_type_options.pack(pady=(10,5))
        self.variety_entry = ctk.CTkEntry(self, placeholder_text=var_name)
        self.variety_entry.pack(pady=5)
        self.index_options = ctk.CTkOptionMenu(self, values=self.type_ranges[self.g_type_options.get()])
        self.index_options.pack(pady=5)
        self.font_size_entry = ctk.CTkEntry(self, placeholder_text='Font Size')
        self.font_size_entry.pack(pady=5)
        self.submit_button = ctk.CTkButton(master=self, text='Submit', command=self.save_variety_index_font)
        self.submit_button.pack(pady=(10,5))
        self.cancel_button = ctk.CTkButton(master=self, text='Cancel', command=self.cancel_update)
        self.cancel_button.pack(pady=(5, 20))


    def g_type_options_callback(self, choice):
        self.index_options.destroy()
        self.submit_button.destroy()
        self.cancel_button.destroy()
        self.index_options = ctk.CTkOptionMenu(self, values=self.type_ranges[self.g_type_options.get()])
        self.index_options.pack(pady=5)
        self.submit_button = ctk.CTkButton(master=self, text='Submit', command=self.save_variety_index_font)
        self.submit_button.pack(pady=(10,5))
        self.cancel_button = ctk.CTkButton(master=self, text='Cancel', command=self.cancel_update)
        self.cancel_button.pack(pady=(5, 20))


    def validate_font(self) -> bool:
        size = self.font_size_entry.get()
        if size in ('', None):
            messagebox.showerror(title='Error', message='Please enter a number for font size')
            return False
        try:
            size_num = int(self.font_size_entry.get())
            if size_num < 12:
                messagebox.showerror(title='Too Small', message='Font size too small. Must be between 12 and 72')
                return False
            if size_num > 72:
                messagebox.showerror(title='Too Big', message='Font size to large. Must be between 12 and 72')
                return False
            return True
        except (ValueError, TypeError):
            messagebox.showerror(title='Error', message='Please enter a positive whole number for font size')
            return False


    def save_variety_index_font(self):
        variety = self.variety_entry.get()
        if variety == '':
            variety = self.variety_entry.cget('placeholder_text')
        if self.validate_font():
            if messagebox.askokcancel(title='Confirm Information', message=f'{variety} will be assigned:\nIndex: {self.index_options.get()}\nFont Size: {self.font_size_entry.get()}\nCorrect?'):
                self.var_indexes.update({variety:int(self.index_options.get())})
                self.font_info['Variety'].update({variety:self.font_size_entry.get()})        
                with open(INDEX_FILEPATH, 'w', encoding=ENCODING) as file:
                    json.dump(self.var_indexes, file, indent=4)
                with open(FONT_INFO_PATH, 'w', encoding=ENCODING) as file:
                    json.dump(self.font_info, file, indent=4)
        self.master.destroy()


    def cancel_update(self):
        self.master.destroy()


class NewSupplierFontInfoWindow(ctk.CTkToplevel):
    def __init__(self, supplier_name:str, *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.geometry('350x350')
        self.title('Assign New Supplier font info.')
        self.view = NewSupplierFontInfoFrame(master=self, supplier_name=supplier_name)
        self.view.pack()
        self.grab_set()


class NewSupplierFontInfoFrame(ctk.CTkFrame):
    def __init__(self, master, supplier_name:str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        with open(FONT_INFO_PATH, 'r', encoding=ENCODING) as file:
            self.font_info:dict = json.load(file)
        self.supplier_entry = ctk.CTkEntry(master=self, placeholder_text=supplier_name)
        self.supplier_entry.pack(pady=(10,5))
        self.font_entry = ctk.CTkEntry(master=self, placeholder_text='Font Size')
        self.font_entry.pack(pady=5)
        self.submit_button = ctk.CTkButton(master=self, text='Submit', command=self.save_supplier_font)
        self.submit_button.pack(pady=(10,5))
        self.cancel_button = ctk.CTkButton(master=self, text='Cancel', command=self.cancel_update)
        self.cancel_button.pack(pady=(5, 20))


    def validate_font(self) -> bool:
        size = self.font_entry.get()
        if size in ('', None):
            messagebox.showerror(title='Error', message='Please enter a number for font size')
            return False
        try:
            size_num = int(self.font_entry.get())
            if size_num < 12:
                messagebox.showerror(title='Too Small', message='Font size too small. Must be between 12 and 72')
                return False
            if size_num > 72:
                messagebox.showerror(title='Too Big', message='Font size to large. Must be between 12 and 72')
                return False
            return True
        except (ValueError, TypeError):
            messagebox.showerror(title='Error', message='Please enter a positive whole number for font size')
            return False
        

    def save_supplier_font(self):
        supplier = self.supplier_entry.get()
        if supplier == '':
            supplier = self.supplier_entry.cget('placeholder_text')
        if self.validate_font():
            if messagebox.askokcancel(title='Confirm Info', message=f'{supplier} will be assigned a font size of {self.font_entry.get()}\nCorrect?'):
                self.font_info['Supplier'].update({supplier:int(self.font_entry.get())})
                with open(FONT_INFO_PATH, 'w', encoding=ENCODING) as file:
                    json.dump(self.font_info, file, indent=4)
        self.master.destroy()


    def cancel_update(self):
        self.master.destroy()


class EOMInventoryWindow(ctk.CTkToplevel):
    def __init__(self, data:pd.DataFrame, loss_data:pd.DataFrame, save_path:Path, *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.data = data
        self.loss_data = loss_data
        self.save_path = save_path
        self.geometry('250x150')
        self.title('Generate End of Month Report')
        self.view = EOMInventoryFrame(master=self, data=self.data, loss_data=self.loss_data, save_path=self.save_path)
        self.view.pack()
        self.grab_set()


class EOMInventoryFrame(ctk.CTkFrame):
    def __init__(self, master, data:pd.DataFrame, loss_data:pd.DataFrame, save_path:Path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.data = data
        self.loss_data = loss_data
        self.save_path = save_path
        self.eom_inv = EOMWarehouseInventory(save_path=self.save_path, data=self.data, loss_data=self.loss_data)
        self.date_options = ctk.CTkOptionMenu(master=self, values=self.eom_inv.get_eom_dates())
        self.date_options.pack(pady=(10,5))
        self.generate_button = ctk.CTkButton(master=self, text='Generate', command=self.generate_report)
        self.generate_button.pack(pady=(5,10))


    def generate_report(self):
        self.eom_inv.eom_time = datetime(self.date_options.get())
        self.eom_inv.save_to_xlsx()
        