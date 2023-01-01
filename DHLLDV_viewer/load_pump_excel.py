"""Load pumps and pipelines from excel

The spreadsheet should have sheets with the following properties:
- Names are _not_ case sensitive
- All named ranges have worksheet scope
- All values are in metric units (m, Hz, kW, m3/sec)
- Sheets without 'pipeline', 'pump, 'driver' in the name are ignored
- One worksheet named 'Pipeline'
    - Have a named range 'Pipeline!name
- One or more worksheets whose name ends in the word 'pump'
    - Have named ranges SomePump!['name', 'design_impeller', 'suction_dia', 'disch_dia','design_speed', 'limited',
    'gear_ratio', 'avail_power','pump_curve']
    - name is any valid python string (be careful of escape sequences)
    - design_impeller, suction_dia, and disch_dia are in m
    - speed is in Hz
    - The limited range can contain the value 'torque', 'power', or 'curve'
    - avail_power is in kW
    - gear_ratio is the pump speed divided by the maximum/rated engine speed
    - The pump_curve range has at least three columns and a header row:
        - Three of the columns have the word 'flow', 'head', or 'power' (not case sensitive) in the first row
        - flow is in m3/sec
        - head is in m.w.c
        - power is in kW
- One or more worksheets matching a pump sheet, with the word pump replaced by the word 'driver' (not case-sensitive)
  in the sheet name. For example, if the pump tab is named "SomePump", then the driver will be 'SomeDriver'.
    - Has named ranges 'SomePump Driver'![name', 'power_curve']
    - name is any valid python string (be careful of escape sequences)
    - power_curve has at least two columns and a header row
        - Two of the columns have the word 'speed' and 'power' in the first row
        - speed is in Hz
        - power is in kW
"""
import openpyxl

from DHLLDV.PumpObj import Pump
from DHLLDV.DriverObj import Driver
from DHLLDV.DHLLDV_Utils import interpDict


def get_range_value(wb: openpyxl.Workbook, sheet_id: int, range_name: str):
    """Get the value from the given range on the given sheet"""
    sheet_name = wb.sheetnames[sheet_id]
    sheet_addr = wb.defined_names.get(range_name, sheet_id).value.split("!")[1]
    return wb[sheet_name][sheet_addr].value


def load_driver_from_worksheet(wb: openpyxl.Workbook, sheet_id: int):
    """Create a driver object from a driver worksheet
    wb: The workbook to load
    sheet_id: The id of the driver sheet in the sheet list
    """
    params = {'name': get_range_value(wb, sheet_id, 'name')}
    my_range = wb.defined_names.get('power_curve', sheet_id)
    speed_col = None
    power_col = None
    cell_range = next(my_range.destinations)  # returns a generator of (worksheet title, cell range) tuples
    rows = wb[wb.sheetnames[sheet_id]][cell_range[1]]
    curve = {}
    for row in rows:
        vals = [c.value for c in row]
        if speed_col is None:  # Assume the first row is a header
            speed_col = next(i for i, c in enumerate(vals) if 'speed' in c.lower())
            power_col = next(i for i, c in enumerate(vals) if 'power' in c.lower())
        else:
            curve[float(vals[speed_col])] = float(vals[power_col])
    params['design_power_curve'] = curve
    return Driver(**params)


def load_pump_from_worksheet(wb: openpyxl.Workbook, sheet_id: int, driver_id: int = None):
    """Create a pump object from a pump worksheet
    wb: The workbook to load
    sheet_id: The id of the pump sheet in the sheet list
    driver_id: The id of any driver in the sheet list, or None if no driver
    """
    single_values = {'name': str,
                     'design_impeller': float,
                     'suction_dia': float,
                     'disch_dia': float,
                     'design_speed': float,
                     'limited': str,
                     'gear_ratio': float,
                     'avail_power': float,
                     }

    params = dict([(k, v(get_range_value(wb, sheet_id, k))) for k, v in single_values.items()])
    my_range = wb.defined_names.get('pump_curve', sheet_id)
    sheet_name = wb.sheetnames[sheet_id]
    flow_col = None
    head_col = None
    power_col = None
    cell_range = next(my_range.destinations)  # returns a generator of (worksheet title, cell range) tuples
    rows = wb[sheet_name][cell_range[1]]
    QH = {}
    QP = {}
    for row in rows:
        vals = [c.value for c in row]
        if flow_col is None:    # Assume the first row is a header
            flow_col = next(i for i, c in enumerate(vals) if 'flow' in c.lower())
            head_col = next(i for i, c in enumerate(vals) if 'head' in c.lower())
            power_col = next(i for i, c in enumerate(vals) if 'power' in c.lower())
        else:
            QH[float(vals[flow_col])] = float(vals[head_col])
            QP[float(vals[flow_col])] = float(vals[power_col])
    params['design_QH_curve'] = interpDict(QH)
    params['design_QP_curve'] = interpDict(QP)
    if driver_id is not None:
        params['driver'] = load_driver_from_worksheet(wb, driver_id)
        params['driver_name'] = params['driver'].name
    return Pump(**params)


if __name__ == "__main__":
    fname = "static/pipelines/Example_input.xlsx"

    wb = openpyxl.load_workbook(filename=fname, data_only=True) # Loading a workbook, data_only takes the stored values
    pumps = {}
    drivers = {}
    for ws_name in wb.sheetnames:
        sheet_id = wb.sheetnames.index(ws_name)       # The id / index of a worksheet
        ret_val = ''
        if 'pipeline' in ws_name.lower():
            input_type = 'pipeline'
            pipeline_name = get_range_value(wb, sheet_id, 'name')
            print(f'Pipeline: {pipeline_name}')
        elif 'pump' in ws_name.lower():
            input_type = 'pump'
            pumps[ws_name.lower().removesuffix('pump')] = sheet_id
        elif 'driver' in ws_name.lower():
            input_type = 'driver'
            drivers[ws_name.lower().removesuffix('driver')] = sheet_id
        else:
            input_type = ws_name
        print(f'{sheet_id} {input_type}: {wb[ws_name]}')        # Accessing individual worksheets
        print(wb.defined_names.localnames(sheet_id))  # Range names in a worksheet
        print(ret_val)
    for pump_name in pumps:
        print(pump_name)
        if pump_name in drivers:
            print(load_pump_from_worksheet(wb, pumps[pump_name], drivers[pump_name]))
        else:
            print(load_pump_from_worksheet(wb, pumps[pump_name], None))
