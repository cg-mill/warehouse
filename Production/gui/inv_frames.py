import customtkinter as ctk
import pandas as pd
from tkinter import messagebox
import json

from Inventory import GrainVariety, WarehouseGrainInventory

INDEX_FILEPATH = 'Production/Inventory/data/variety_index.json'
LOW_STOCK_INFO_PATH = 'Production/Inventory/data/ls.json'
ENCODING = 'utf-8'


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
        self.cancel_button.pack(pady=(5,30)) #TODO
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

        
class DetailedViewFrame(ctk.CTkFrame):
    def __init__(self, master, data:pd.DataFrame, **kwargs):
        super().__init__(master, **kwargs)#TODO
        pass


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


class NewVarietyIndexWindow(ctk.CTkToplevel):
    def __init__(self, *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.geometry('350x350')
        self.title('Add Variety to Index')
        self.view = NewVarietyIndexFrame(master=self)
        self.view.pack()
        self.grab_set()
        

class NewVarietyIndexFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        with open(INDEX_FILEPATH, 'r', encoding=ENCODING) as file:
            self.var_indexes:dict = json.load(file)
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
        self.variety_entry = ctk.CTkEntry(self, placeholder_text='Variety')
        self.variety_entry.pack(pady=5)
        self.index_options = ctk.CTkOptionMenu(self, values=self.type_ranges[self.g_type_options.get()])
        self.index_options.pack(pady=5)
        self.submit_button = ctk.CTkButton(master=self, text='Submit', command=self.save_variety_index)
        self.submit_button.pack(pady=(10,5))
        self.canel_button = ctk.CTkButton(master=self, text='Cancel', command=self.cancel_update)
        self.canel_button.pack(pady=(5, 20))

    def g_type_options_callback(self, choice):
        self.index_options.destroy()
        self.index_options = ctk.CTkOptionMenu(self, values=self.type_ranges[self.g_type_options.get()])
        self.index_options.pack()


    def save_variety_index(self):
        #TODO open window to confirm choice
        self.var_indexes.update({self.variety_entry.get():self.index_options.get()})
        with open(INDEX_FILEPATH, 'w', encoding=ENCODING) as file:
            json.dump(self.var_indexes, file, indent=4)
        self.master.destroy()


    def cancel_update(self):
        self.master.destroy()
        

class VarietyIndexOptions(ctk.CTkFrame):
    def __init__(self, master, types_idex:dict, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.g_type_options = ctk.CTkOptionMenu(self, values=types_idex.keys())
        self.variety_entry = ctk.CTkEntry()
        self.index_options = ctk.CTkOptionMenu()
        #TODO


class NewVarietyFontInfoWindow(ctk.CTkFrame):
    pass #TODO


class NewVarietyFontInfoFrame(ctk.CTkFrame):
    pass #TODO