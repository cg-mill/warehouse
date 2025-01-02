import customtkinter as ctk


class TimeInput(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.hour_input = ctk.CTkComboBox(
            master=self, 
            values=[str(hour) for hour in range(1,13)],
            width=60,
            )
        self.hour_input.grid(row=0, column=0)
        minutes = []
        for time in range(0, 56, 5):
            if len(str(time)) < 2:
                minutes.append(f'0{time}')
            else: 
                minutes.append(str(time))
        self.minute_input = ctk.CTkComboBox(
            master=self,
            values=minutes,
            width=60
        )
        self.minute_input.grid(row=0, column=1)
        self.am_pm = ctk.CTkComboBox(master=self, values=['AM', 'PM'], width=60)
        self.am_pm.grid(row=0, column=2)


class MoistureProteinInput(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.m_label = ctk.CTkLabel(master=self, text='M')
        self.m_label.grid(row=0, column=0)
        self.m_input = ctk.CTkEntry(master=self, placeholder_text='%', width=60)
        self.m_input.grid(row=0, column=1)
        self.p_label = ctk.CTkLabel(master=self, text='P')
        self.p_label.grid(row=0, column=2)
        self.p_input = ctk.CTkEntry(master=self, placeholder_text='%', width=60)
        self.p_input.grid(row=0, column=3)
