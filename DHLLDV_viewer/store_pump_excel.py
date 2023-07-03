"""Store pipelines to Excel

Create an excel file with the format defines in load_pump_excel

Added by R. Ramsdell 2023-07-02"""

import copy
import openpyxl
import os.path
import string

from DHLLDV.DriverObj import Driver
from DHLLDV.PumpObj import Pump
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.SlurryObj import Slurry
from DHLLDV.DHLLDV_Utils import interpDict

from DHLLDV_viewer.load_pump_excel import excel_requireds
from DHLLDV_viewer.load_pump_excel import __doc__ as xl_doc


excel_requireds_param_map = {'pipeline': {'name': 'name',
                                          },
                             'slurry': {'name': 'name',
                                        'pipe_dia': 'Dp',
                                        'd_50': 'D50',
                                        'fluid': str,
                                        'Cv': float,
                                        'rhos': float,
                                        'rhoi': float
                                        },
                             'pump': {'name': str,
                                      'design_impeller': float,
                                      'suction_dia': float,
                                      'disch_dia': float,
                                      'design_speed': float,
                                      'limited': str,
                                      'gear_ratio': float,
                                      'avail_power': float,
                                      },
                             'driver': {'name': str,
                                        }
                             }

# These are the characters allowed in filenames when saving to excel
valid_filename_chars = f'-_{string.ascii_letters}{string.digits}'
replace_filename_chars = ('.', ' ')  # These will be replaced with '_'


def remove_disallowed_filename_chars(filename_candidate: str, extension:str) -> str:
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
    wb[sheet_name][range_addr].value = value
    sheet_id = wb.sheetnames.index(sheet_name)
    wb.create_named_range(range_name, worksheet=wb[sheet_name], value=range_addr, scope=sheet_id)


def write_slurry_to_excel(wb: openpyxl.workbook, slurry: Slurry) -> None:
    """Write a slurry to the workbook"""
    sheet_name = 'slurry'
    ws = wb.create_sheet(sheet_name)
    sheet_id = wb.sheetnames.index(sheet_name)  # The id / index of a worksheet


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
        ws.cell(row=current_row, column=1, value=row)
        current_row += 1
    for sheet_name, req_data in requireds.items():
        ws = wb.create_sheet(sheet_name)
        sheet_id = wb.sheetnames.index(sheet_name)  # The id / index of a worksheet
        current_row = 1
        for req_data, type in requireds[sheet_name].items():  # Create the range names
            if type in [str, float]:  # But not for the 'required' field or tables
                create_and_fill_named_range(wb, sheet_name, req_data, f'B{current_row}', req_data)
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