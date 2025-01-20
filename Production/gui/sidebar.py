import customtkinter as ctk
import pandas as pd

from gui import ReceivingWindow, NewVarietyIndexWindow
from Inventory import TotalInventory, WarehouseGrainInventory

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class HomeSideBar(ctk.CTkFrame):
    def __init__(self, master:'App', data:pd.DataFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.data = data
        self.master = master
        #TODO set GoHAACP credentials, seve to json
        #TODO Generate End of Month Inventory
        #TODO Set index for new varieties
        self.inv_label = ctk.CTkLabel(self, text='Inventory', anchor='nw')
        self.inv_label.grid(row=0, column=0)
        self.inv_dropdown = ctk.CTkOptionMenu(
            self, 
            values=['Low Stock', 'Quick View', 'Detailed View']
            )
        self.inv_dropdown.grid(row=1, column=0)
        self.set_low_stock_button = ctk.CTkButton(self, text='Set Low Stock Levels')
        self.set_low_stock_button.grid(row=2, column=0, pady=10)

        self.receiving_label = ctk.CTkLabel(self, text='Receiving', anchor='nw')
        self.receiving_label.grid(row=3, column=0, pady=(25,0))
        self.new_receiving_button = ctk.CTkButton(
            self, 
            text='New Report', 
            command=self.open_new_receiving_window
            )
        self.new_receiving_button.grid(row=4, column=0, pady=5)
        self.load_receiving_button = ctk.CTkButton(
            self, 
            text='Load Report', 
            command=self.load_receiving_window
            )
        self.load_receiving_button.grid(row=5, column=0, pady=5)
    
        self.totals_label = ctk.CTkLabel(self, text='', anchor='w', height=150, justify='left')
        self.totals_label.grid(row=6, column=0, pady=10)
        self.nv_index_button = ctk.CTkButton(self, text='Add New Variety to Index', anchor='w', height=50, command=self.open_new_variety_index_form)
        self.nv_index_button.grid(row=7, column=0, pady=10)
        self.error_label = ctk.CTkLabel(self, text='errors', anchor='sw', height=50)
        self.error_label.grid(row=8, column=0)

        self.receiving_window:ctk.CTkToplevel = None
        self.nv_index_window:ctk.CTkToplevel = None


    def set_totals_label(self, data:pd.DataFrame):#tot_inv:TotalInventory):
        tot_inv = TotalInventory(data=data)
        working_totes = [tote for tote in tot_inv.all_totes if not tote.is_killed]
        totals_str = f'Total Weight: {tot_inv.total_weight}\n'
        totals_str += f'Total Totes: {len(working_totes)}\n'
        totals_str += f'Total Value: ${tot_inv.total_value:.2f}'
        self.totals_label.configure(text=totals_str)


    def open_new_receiving_window(self):
        if self.receiving_window is None or not self.receiving_window.winfo_exists():
            self.receiving_window = ReceivingWindow(
                data=self.data,
                inv_path=self.master.inv_path,
                receiving_path=self.master.receiving_path,
                tote_label_path=self.master.tote_label_path,
                loss_log_path=self.master.loss_log_path
                )
        
            # self.error_label.bind(self.receiving_window.status_var) #FIXME
        else:
            self.receiving_window.focus()


    def open_new_variety_index_form(self): #FIXME widgets reorder when switching grain types
        if self.nv_index_window is None or not self.nv_index_window.winfo_exists():
            self.nv_index_window = NewVarietyIndexWindow()
        else:
            self.nv_index_window.focus()


    def update_gohaacp_creds():
        pass #TODO    

    def load_receiving_window(self):
        pass #TODO