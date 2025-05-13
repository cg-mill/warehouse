import customtkinter as ctk
import pandas as pd

from gui import ReceivingWindow, NewVarietyWindow, EOMInventoryWindow
from Inventory import TotalInventory, EOMWarehouseInventory, WarehouseGrainInventory

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class HomeSideBar(ctk.CTkFrame):
    def __init__(self, master:'App', data:pd.DataFrame, loss_data:pd.DataFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.data = data
        self.loss_data = loss_data
        self.master = master
        #TODO set GoHAACP credentials, seve to json
        #TODO Generate End of Month Inventory
        #TODO remove load report
        self.inv_label = ctk.CTkLabel(self, text='Inventory', anchor='nw')
        self.inv_label.grid(row=0, column=0)
        self.inv_dropdown = ctk.CTkOptionMenu(
            self, 
            values=['Low Stock', 'Quick View']
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
        self.end_of_month_label = ctk.CTkLabel(self, text='End of Month Report', anchor='nw')
        self.end_of_month_label.grid(row=5, column=0, pady=(10,5))
        self.end_of_month_button = ctk.CTkButton(self, text='Generate EOM Report', command=self.open_eom_window)
        self.end_of_month_button.grid(row=6, column=0, pady=5)
    
        self.totals_label = ctk.CTkLabel(self, text='', anchor='w', height=150, justify='left')
        self.totals_label.grid(row=7, column=0, pady=10)

        self.receiving_window:ctk.CTkToplevel = None
        self.eom_window:ctk.CTkToplevel = None


    def set_totals_label(self, data:pd.DataFrame):
        total_inv = TotalInventory(data=data)
        working_totes = [tote for tote in total_inv.all_totes if not tote.is_killed]
        totals_str = f'Total Weight: {total_inv.total_weight}\n'
        totals_str += f'Total Totes: {len(working_totes)}\n'
        totals_str += f'Total Value: ${total_inv.total_value:.2f}'
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
        else:
            self.receiving_window.focus()


    def open_new_variety_index_form(self): #FIXME remove?
        if self.nv_index_window is None or not self.nv_index_window.winfo_exists():
            self.nv_index_window = NewVarietyWindow()
        else:
            self.nv_index_window.focus()

        
    def open_eom_window(self):
        if self.eom_window is None or not self.eom_window.winfo_exists():
            self.eom_window = EOMInventoryWindow(data=self.data, loss_data=self.loss_data, save_path=self.master.eom_save_path)
        else:
            self.eom_window.focus()


    def update_gohaacp_creds():
        pass #TODO 
