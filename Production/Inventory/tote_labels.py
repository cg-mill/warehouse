import json
import docx
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor
from win32 import win32api
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Inventory import Tote, TotalInventory


FONT_SIZE_INFO_PATH = 'Production/Inventory/data/font_info.json'
ENCODING = 'utf-8'


class LabelMaker:
    def __init__(self):
        self.font_info = self.load_font_info()


    def load_font_info(self) -> dict:
        try:
            with open(FONT_SIZE_INFO_PATH, 'r', encoding=ENCODING) as file:
                font_info = json.load(file)
                return font_info
        except FileNotFoundError:
            print('File not found')
            return {}
    

    def _set_word_font_sizes_console(self, inv:'TotalInventory'):
        font_dict = {
            "Variety": {
                variety : int(input(f'Font Size for Variety -- {variety}:\n')) for variety in inv.get_all_varieties()
            },
            "Supplier": {
                supplier : int(input(f'Font Size for Supplier -- {supplier}:\n')) for supplier in inv.get_all_suppliers()
            }
        }
        with open(FONT_SIZE_INFO_PATH, 'w', encoding=ENCODING) as file:
            json.dump(font_dict, file, indent=4)


    def variety_to_print(self, tote:'Tote') -> str: #TODO test
        if tote.grain_type in ['Wheat', 'Buckwheat']:
            return tote.variety
        elif tote.grain_type == 'Rice':
            return f'{tote.grain_type}, {tote.variety}'
        else:
            return f'{tote.variety} {tote.grain_type}'
    

    def make_label(self, tote:'Tote', path:Path):
        FONT_NAME = 'Calibri (Body)'
        LG_FONT = Pt(72)
        SM_FONT = Pt(37)
        ORG_FONT_SIZE = Pt(78)
        NOT_ORG_FONT_SIZE = Pt(70)
        LG_LINE_SPACING = 0.88
        SM_LINE_SPACING = 0.76

        doc = docx.Document()
        
        section = doc.sections[0]
        width = section.page_width
        height = section.page_height
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_height = width
        section.page_width = height
        section.top_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.3)
        section.bottom_margin = Inches(0.5)
        
        
        tote_num_par = doc.add_paragraph().add_run(f'Tote # {tote.tote_num}')
        tote_num_par.font.size = LG_FONT
        tote_num_par.font.name = FONT_NAME

        var_par = doc.add_paragraph()
        var_label = var_par.add_run('Variety: ')
        var_label.font.name = FONT_NAME
        var_label.font.size = LG_FONT

        variety = var_par.add_run(self.variety_to_print(tote))
        variety.font.name = FONT_NAME
        variety.font.size = Pt(self.font_info['Variety'][tote.variety])

        sup_par = doc.add_paragraph()
        sup_label = sup_par.add_run('Farmer: ')
        sup_label.font.name = FONT_NAME
        sup_label.font.size = LG_FONT
        supplier = sup_par.add_run(tote.supplier)
        supplier.font.name = FONT_NAME
        supplier.font.size = Pt(self.font_info['Supplier'][tote.supplier])

        date_par = doc.add_paragraph().add_run(f'Date Received: {tote.date_received.strftime('%m/%d/%Y')}')
        date_par.font.size = SM_FONT
        date_par.font.name = FONT_NAME
        
        m_p_par = doc.add_paragraph()
        if tote.moisture > 0.0:
            m_p_par.add_run(f'Moisture: {tote.moisture:.2f}%')
        else:
            m_p_par.add_run(f'Moisture:')
        m_p_par.paragraph_format.tab_stops.add_tab_stop(Inches(5.5))
        m_p_par.add_run().add_tab()

        if tote.protein > 0.0:
            m_p_par.add_run(f'Protein: {tote.protein:.2f}%')
        else:
            m_p_par.add_run('Protein:')
        for run in m_p_par.runs:
            run.font.size = SM_FONT
            run.font.name = FONT_NAME
        date_weight_par = doc.add_paragraph()
        if tote.is_clean:
            tabs = 5
            date_weight_par.add_run(f'Clean Date: COA{'\t'*tabs}Clean Weight:{tote.weight}')  
        else:
            tabs = 7
            date_weight_par.add_run(f'Clean Date:{'\t'*tabs}Clean Weight:')
        date_weight_par.runs[0].font.size = SM_FONT
        date_weight_par.runs[0].font.name = FONT_NAME

        map_co2_par = doc.add_paragraph().add_run(f'MAP Date:\t\t\t\t\t\t\tC02%:')
        map_co2_par.font.size = SM_FONT
        map_co2_par.font.name = FONT_NAME

        org_par = doc.add_paragraph()
        org_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if tote.is_org:
            org_par.add_run('CERTIFIED ORGANIC')
            org_par.runs[0].font.size = ORG_FONT_SIZE
            org_par.runs[0].font.color.rgb = RGBColor(0, 160, 56)
        else:
            org_par.add_run('NOT CERTIFIED ORGANIC')
            org_par.runs[0].font.size = NOT_ORG_FONT_SIZE
            org_par.runs[0].font.color.rgb = RGBColor(255, 75, 75)
        org_par.runs[0].font.name = FONT_NAME

        for i in range(len(doc.paragraphs)):
            if i in [0, 1, 2, len(doc.paragraphs) - 1]:
                doc.paragraphs[i].paragraph_format.line_spacing = LG_LINE_SPACING
            else:
                doc.paragraphs[i].paragraph_format.line_spacing = SM_LINE_SPACING

        doc.save(f'{path}/{tote.tote_num}.docx')


    def print_tote(self, file: Path, directory_path: Path):#FIXME rework? get rid of popups, out of order
        win32api.ShellExecute(
            0,
            'print',
            file.as_posix(),
            None, 
            directory_path.as_posix(),
            0
        )

    
    def print_directory(self, directory_path: Path):
        for file in directory_path.iterdir():
            for _ in range(2):
                self.print_tote(file=file, directory_path=directory_path)