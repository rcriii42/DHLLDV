"""Load pumps and pipelines from excel

The spreadsheet should have sheets with the following properties:
- Names are _not_ case sensitive
- All named ranges have worksheet scope
- All values are in metric units (m, Hz, kW, m3/sec)
- Sheets without 'pipeline', 'pump, 'driver' in the name are ignored
- One worksheet named 'Pipeline'
    - Have a named range 'Pipeline!pipeline_name
- One or more worksheets with the word 'pump' in the name
    - Have named ranges SomePump!['pump_name', 'impeller', 'suction', 'discharge','speed', 'limited', 'avail_power',
      'pump_curve']
    - pump_name is any valid python string (be careful of escape sequences)
    - impeller, suction, and discharge are in m
    - speed is in Hz
    - The limited range can contain the value 'torque', 'power', or 'curve'
    - The pump_curve range has at least three columns and a header row:
        - Three of the columns have the word 'flow', 'head', or 'power' (not case sensitive) in the first row
        - flow is in m3/sec
        - head is in m.w.c
        - power is in kW
- One or more worksheets matching a pump sheet, with the word pump replaced by the word 'driver' (not case-sensitive)
  in the sheet name. For example, if the pump tab is named "SomePump", then the driver will be 'SomeDriver'.
    - Has named ranges 'SomePump Driver'!['driver_name', 'gear_ratio', 'power_curve']
    - driver_name is any valid python string (be careful of escape sequences)
    - gear_ratio is the pump speed divided by the maximum/rated engine speed
    - power_curve has at least two columns and a header row
        - Two of the columns have the word 'speed' and 'power' in the first row
        - speed is in Hz
        - power is in kW
"""
import openpyxl

from DHLLDV.PumpObj import Pump


def get_range_value(wb: openpyxl.Workbook, sheet_id: int, range_name: str):
    """Get the value from the given range on the given sheet"""
    sheet_name = wb.sheetnames[sheet_id]
    name_cell = wb.defined_names.get(range_name, sheet_id).value.split("!")[1]
    return wb[sheet_name][name_cell].value


def load_pump_from_worksheet(wb: openpyxl.Workbook, sheet_id: int):
    """Create a pump object from a pump worksheet
    wb: The workbook to load
    sheet_id: The id of the pump sheet in the sheet list
    """
    single_values = {'pump_name': str,
                     'impeller': float,
                     'suction': float,
                     'discharge': float,
                     'limited': str,
                     'avail_power': float,}
    return {(k, v(get_range_value(wb, sheet_id, k))) for k, v in single_values.items()}


if __name__ == "__main__":
    fname = "static/pipelines/Example_input.xlsx"

    wb = openpyxl.load_workbook(filename=fname, data_only=True) # Loading a workbook
    print(wb.sheetnames)                        # Names of worksheets
    for ws_name in wb.sheetnames:
        sheet_id = wb.sheetnames.index(ws_name)       # The id / index of a worksheet
        ret_val = ''
        if 'pipeline' in ws_name.lower():
            input_type = 'pipeline'

        elif 'pump' in ws_name.lower():
            input_type = 'pump'
            ret_val = load_pump_from_worksheet(wb, sheet_id)
        elif 'driver' in ws_name.lower():
            input_type = 'driver'
        else:
            input_type = ws_name
        print(f'{sheet_id} {input_type}: {wb[ws_name]}')        # Accessing individual worksheets
        print(wb.defined_names.localnames(sheet_id))  # Range names in a worksheet
        print(ret_val)