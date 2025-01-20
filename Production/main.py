from typing import Any, Literal, Tuple
from typing_extensions import Literal
import customtkinter as ctk
import pandas as pd
from datetime import datetime
from tkinter import messagebox
from pathlib import Path

from Inventory import (
    GrainVariety, 
    WarehouseGrainInventory,
    Crop, 
    TotalInventory
)
from gui import (
    ReceivingWindow,
    ReceivingFrame,
    QuickViewFrame, 
    LowStockFrame, 
    LowStockEditFrame,
    DetailedViewFrame,
    HomeSideBar
)


INVENTORY_PATH = 'TESTING FILES/Warehouse Inventory.xlsm' # FOR HOME / TESTING
# INVENTORY_PATH = Path(Path().home(), '/Team BSM Dropbox/Warehouse/Warehouse Inventory.xlsm')
RECEIVING_PATH = 'TESTING FILES/The Receiving Log - 2022 to Current.xlsx' # temp path
# RECEIVING_PATH = Path(Path().home(), '/Team BSM Dropbox/Food Safety/Receiving/The Receiving Log - 2022 to Current.xlsx')
LOSS_LOG_PATH = 'TESTING FILES/Receiving - Cleaning Loss.xlsx'
# LOSS_LOG_PATH = Path(Path().home(), '/Team BSM Dropbox/Warehouse/Receiving - Cleaning Loss.xlsx')
TOTE_LABEL_SAVE_PATH = Path(Path().home(), "Desktop") # temp path


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.inv_path = INVENTORY_PATH
        self.receiving_path = RECEIVING_PATH
        self.tote_label_path = TOTE_LABEL_SAVE_PATH
        self.loss_log_path = LOSS_LOG_PATH
        self.data = self.get_data(path=self.inv_path)
        
        self.geometry('900x550')
        self.title('Warehouse Operations')
        # self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        self.refresh_button = ctk.CTkButton(master=self, text='Refresh', command=self.refresh, height=25, width = 100)
        self.refresh_button.grid(row=0, column=0)
        self.sidebar = HomeSideBar(master=self, data=self.data, width=100, height=self._current_height)
        self.sidebar.grid(row=1, column=0, rowspan=1, sticky='nw', pady=15)
        self.sidebar.set_totals_label(data=self.data)
        self.sidebar.inv_dropdown.configure(command=self.inv_dropdown_callback)
        self.sidebar.set_low_stock_button.configure(command=self.set_low_stock_callback)
        
        self.inv_view = LowStockFrame(master=self, data=self.data, height=self._current_height, width=700)
        self.inv_view.grid(row=0, column=1, rowspan=2, sticky='ns')


    def inv_dropdown_callback(self, choice):
        self.inv_view.destroy()
        if choice == 'Quick View':
            self.inv_view = QuickViewFrame(master=self, data=self.data, height=self._current_height, width=700)
        elif choice == 'Detialed View':
            pass
        else:
            self.inv_view = LowStockFrame(master=self, data=self.data, height=self._current_height, width=700)  
        self.inv_view.grid(row=0, column=1, rowspan=2, sticky='ns')


    def set_low_stock_callback(self):
        self.inv_view.destroy()
        self.inv_view = LowStockEditFrame(master=self, data=self.data, height=self._current_height, width=700)
        self.inv_view.grid(row=1, column=1, rowspan=2, sticky='ns')
        self.inv_view.cancel_button.configure(command=self.low_stock_edit_cancel)


    def low_stock_edit_cancel(self):
        self.inv_view.destroy()
        self.inv_view:ctk.CTkScrollableFrame = self.inv_dropdown_callback(self.sidebar.inv_dropdown.get())
        self.inv_view.grid(row=0, column=1, rowspan=2, sticky='ns')


    def refresh(self):
        self.data = self.get_data(path=self.inv_path)
        self.inv_view = self.inv_dropdown_callback(choice=self.sidebar.inv_dropdown.get())


    def get_data(self, path) -> pd.DataFrame:
        data =  pd.read_excel(
            path,
            index_col=False,
            sheet_name='All',
            usecols='A:N,P,Q',
            engine='openpyxl',
            # parse_dates=['Date Received','Clean Date','MAP Date', 'Kill Date']
            )
        data.dropna(subset=['Tote #'], inplace=True)
        # data.fillna(value=0, axis='COGs', inplace=True)
        return data



if __name__ == '__main__':
    app = App()
    app.mainloop()