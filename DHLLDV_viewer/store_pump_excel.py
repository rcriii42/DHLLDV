"""Store pipelines to Excel

Create an excel file with the format defines in load_pump_excel

Added by R. Ramsdell 2023-07-02"""

import openpyxl
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import quote_sheetname, absolute_coordinate
import os.path
import string

from DHLLDV.DriverObj import Driver
from DHLLDV.PumpObj import Pump
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.SlurryObj import Slurry
from DHLLDV.DHLLDV_Utils import interpDict

from DHLLDV_viewer.load_pump_excel import excel_requireds
from DHLLDV_viewer.load_pump_excel import __doc__ as xl_doc


# These are the characters allowed in filenames when saving to excel
valid_filename_chars = f'-_{string.ascii_letters}{string.digits}'
replace_filename_chars = ('.', ' ')  # These will be replaced with '_'


def remove_disallowed_filename_chars(filename_candidate: str, extension: str) -> str:
    """Turn a string into an acceptable filename using a whitelist approach

    '.' and ' ' become '_', other unwanted characters are removed

    filename_candidate is the string to be transformed
    extension is the filename extension to add

    Returns the cleaned filename
    """
    for c in replace_filename_chars:
        cleaned_filename = filename_candidate.replace(c, '_')
    cleaned_filename = ''.join(c for c in cleaned_filename if c in valid_filename_chars)
    cleaned_filename += extension
    # cleaned_filename = unicodedata.normalize('NFKD', cleaned_filename).encode('ASCII', 'ignore')
    return cleaned_filename


def create_and_fill_named_range(wb: openpyxl.Workbook, sheet_name: str or None, range_name: str, range_addr: str,
                                value: str or float) -> None:
    """Create a named range and fill with the given value

    wb: The workbook
    sheet_name: The sheet to scope the range to, or None for workbook scope
    range_name: The name of the defined name, must meet excel rules
    range_addr: The cell address in excel "A1" format
    value: The value to place in the cell
    """
    ws = wb[sheet_name]
    ws[range_addr].value = value
    ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate(range_addr)}"
    defn = DefinedName(range_name, attr_text=ref)
    ws.defined_names.add(defn)


def write_slurry_to_excel(wb: openpyxl.workbook, slurry: Slurry, reqs: dict) -> None:
    """Write a slurry to the workbook

    wb: The Workbook
    slurry: The Slurry to write
    reqs: The 'slurry' dict from excel_requireds
    """
    sheet_name = 'slurry'
    current_row = 1
    units_map = {'name': '',
                 'pipe_dia': 'm',
                 'd_15': 'mm',
                 'd_50': 'mm',
                 'd_85': 'mm',
                 'fluid': 'fresh/salt',
                 'Cv': '-',
                 'rhos': "ton/m3",
                 'rhoi': "ton/m3"}
    for range_name, val_type in reqs.items():
        if range_name == 'required':
            continue
        elif 'd_' in range_name:
            value = slurry.get_dx(float(range_name[2:])/100)*1000
        elif range_name == 'pipe_dia':
            value = slurry.Dp
        else:
            try:
                value = slurry.__dict__[range_name]
            except KeyError:
                value = slurry.__dict__[f'_{range_name}']  # Several parameters have shadow "_xxx" variables
        wb['slurry'][f'A{current_row}'].value = range_name
        create_and_fill_named_range(wb, sheet_name, range_name, f'B{current_row}', value)
        wb['slurry'][f'C{current_row}'].value = units_map[range_name]
        current_row += 1


def write_pump_to_excel():
    pass


def write_pipesections_to_excel(wb: openpyxl.workbook, pipesections: list[Pipe, Pump], current_row: int) -> int:
    """Write the pipe section table to the workbook

    wb: The Workbook
    pipesections: The list of Pipe or Pump objects
    current_row: The row to start writing
    """
    sheet_name = 'pipeline'
    sheet_id = wb.sheetnames.index(sheet_name)
    current_col = 1
    for header in ('Pipe Name', 'Diameter (m)', 'Length (m)', 'Total K', 'Elev Change (m)', 'Final Elev (m)'):
        wb[sheet_name].cells()


def store_to_excel(pipeline: Pipeline, requireds: dict or None = None, path="static/pipelines") -> str:
    """Store the pipeline to a new excel file

    The filename will be a version of the pipeline name

    pipeline: The pipeline to store
    requireds: A dict with the layout of the file. If NOne, use excel_requireds defined above
    path: The folder path (relative to .) for saving

    TODO: returns (fname or workbook?)
    """
    fname = os.path.join(path, remove_disallowed_filename_chars(pipeline.name, '.xlsx'))
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'documentation'
    current_row = 1
    for row in xl_doc.split('\n')[2:]:
        cell_addr = f'A{current_row}'
        ws[cell_addr].value = row
        current_row += 1
    for sheet_name, req_data in requireds.items():
        wb.create_sheet(sheet_name)
        if sheet_name == 'slurry':
            write_slurry_to_excel(wb, pipeline.slurry, req_data)
        else:
            current_row = 1
            for range_name, data_type in requireds[sheet_name].items():  # Create the range names
                if data_type in [str, float]:  # But not for the 'required' field or tables
                    create_and_fill_named_range(wb, sheet_name, range_name, f'B{current_row}', range_name)
                    current_row += 2
    wb.save(fname)

    wb.close()
    return fname


if __name__ == "__main__":
    import datetime
    from DHLLDV_viewer.load_pump_excel import load_pipeline_from_workbook
    in_fname = "static/pipelines/Example_input.xlsx"
    wb = openpyxl.load_workbook(filename=in_fname, data_only=True)  # Loading a workbook, data_only takes the stored values
    PL = load_pipeline_from_workbook(wb)
    PL.name = f'Example Stored Pipeline: {datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")}'
    new_PL_xl_name = store_to_excel(PL, excel_requireds)

    new_wb = openpyxl.load_workbook(filename=new_PL_xl_name, data_only=True)
    new_PL = load_pipeline_from_workbook(new_wb)
