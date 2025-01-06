from datetime import datetime
# from email.mime.message import MIMEMessage
# from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # from inventory_obj import WarehouseGrainInventory, GrainVariety
    from Inventory import WarehouseGrainInventory, GrainVariety

SUBJECT = 'Working Inventory Update'
APP_PASS = os.environ.get('EMAIL_APP_PASS')


class Mailer:
    def __init__(
            self, 
            inventory:'WarehouseGrainInventory',
            send_from:str,
            send_to:list[str]
            ) -> None:
        self.sender = send_from
        self.send_to = send_to
        self.inventory = inventory

        self.main_grain_types = ['Wheat', 'Rye', 'Corn']

        self.message = MIMEMultipart()
        self.message["Subject"] = f'{SUBJECT} | {self.inventory.time}'
        self.message["From"] = self.sender
        self.message["To"] = ', '.join(self.send_to)

        self.html = f"""\
        <html>
        <body>
        <p><i>All weight in pounds</i></p>
            {self.format_message_body_html()}
            <h4><i>Approx. Total Inventory Weight</i></h4><p>{self.inventory.total_weight}</p>
        </body>
        </html>
        """
        self.main_body = MIMEText(self.html, 'html')
        self.message.attach(self.main_body)


    def format_variety_html_table(self, grain_variety:'GrainVariety', include_type:bool = True) -> str:
        if include_type == False or grain_variety.variety == grain_variety.type:
            formatted_str = f'<h3>{grain_variety.variety}:</h3>'
        else:
            formatted_str = f'<h3>{grain_variety.type}, {grain_variety.variety}:</h3>'
        
        formatted_str += f'''
        <table border="1" cellpadding="5" style="border: 2px solid black; border-collapse: collapse; width:35%">
            <tr align="center">
                <th></th> 
                <th>Organic</th>
                <th>Non-Organic</th>
                <th>Seed Stock</th>
            </tr>
            <tr align="center">
                <td><b>Totes</b></td>
                <td>{grain_variety.org_totes}</td>
                <td>{grain_variety.non_organic_totes}</td>
                <td>{grain_variety.seed_stock_totes}</td>
            </tr>
            <tr align="center">
                <td><b>Weight</b></td>
                <td>{grain_variety.org_weight}</td>
                <td>{grain_variety.non_organic_weight}</td>
                <td>{grain_variety.seed_stock_weight}</td>
            </tr>
            <caption>
                <i>Approx Total Weight:</i> {grain_variety.total_weight}
                <br><i>Aprrox Change from {self.get_previous_date()}:</i> {self.get_change_from_previous(grain_variety)}
            </caption>
        </table><br>
        ''' 
        return formatted_str
    

    def format_grain_type_tables(self, grain_type:str) -> str:
        formatted_str = f'<h2><br>{grain_type}</h2>'
        for item in self.inventory.total_inventory:
            for var in self.inventory.working_varieties:
                if item.variety in var and item.type == grain_type:
                    formatted_str += self.format_variety_html_table(item, include_type=False)
        return formatted_str
        

    def format_message_body_html(self) -> str:
        main_grain_types = ['Corn', 'Rye', 'Wheat']
        formatted_str = ''

        if len(self.inventory.ls_varieties) > 0:
            formatted_str += '<div style = "border-top: 2px solid red; border-bottom: 2px solid red">'
            formatted_str += '<h1>Low Stock</h1>'
            for item in self.inventory.ls_varieties:
                formatted_str += self.format_variety_html_table(item)
            formatted_str += '</div>'

        for g_type in main_grain_types:
            formatted_str += self.format_grain_type_tables(g_type)

        misc_varieties = [var for var in self.inventory.total_inventory if var.type not in main_grain_types and var.type != 'Assorted Heirloom Seed Stock']
        if len(misc_varieties) > 0:
            formatted_str += '<h2><br>Misc.</h2>'
            for item in misc_varieties:
                formatted_str += self.format_variety_html_table(item)
        return formatted_str

    
    def send_mail(self):
        with smtplib.SMTP('smtp.gmail.com', port=587) as connetion:
            connetion.starttls()
            connetion.login(user=self.sender, password=APP_PASS)
            for person in self.send_to:
                connetion.sendmail(
                    from_addr=self.sender,
                    to_addrs=person,
                    msg=self.message.as_string()
                )
                print(f'Message Sent To --- {person}')
    

    def get_previous_date(self):
        if len(self.inventory.prev_history) > 0:
            for key in self.inventory.prev_history:
                previous_date = key
            return previous_date
        else:
            return self.inventory.time
        
    def get_change_from_previous(self, grain_variety:'GrainVariety') -> int:
        difference = 0 #TODO check for out of stock varieties
        if len(self.inventory.prev_history) > 0:
            data = self.inventory.prev_history[self.get_previous_date()]
            for dict in data:
                if dict['variety'] == grain_variety.variety:
                    difference = grain_variety.total_weight - dict['total_weight']
                    break
                if dict == data[-1]:
                    return f'+{grain_variety.total_weight}'
            if difference > 0:
                return f'+{difference}'
            else:
                return difference
        else:
            return difference
        
    def attach_eom_inventory(self):
        pass #TODO

    

###################### For List of All Previous Inventories ##################################
    # def get_previous_date(self):
    #     if len(self.inventory.inv_history) > 0:
    #         data = self.inventory.inv_history[-1]
    #         for key in data:
    #             previous_date = key
    #         return previous_date
    #     else:
    #         return self.inventory.time

    # def get_change_from_previous(self, grain_variety:GrainVariety): 
    #     if len(self.inventory.inv_history) > 0:
    #         data = self.inventory.inv_history[-1]
    #         previous_inv = data[self.get_previous_date()]
    #         for dict in previous_inv:
    #             if dict['variety'] == grain_variety.variety:
    #                 difference = grain_variety.total_weight - dict['total_weight']
    #         if difference > 0:
    #             return f'+{difference}'
    #         else:
    #             return difference
    #     else:
    #         return 0
