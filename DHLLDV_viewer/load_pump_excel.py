"""Load pumps and pipelines from excel

The spreadsheet should have sheets with the following properties:
- Names are _not_ case sensitive
- All named ranges have worksheet scope
- All values are in metric units (m, Hz, kW, m3/sec)
- Sheets without 'pipeline', 'pump, 'driver' in the name are ignored
- One worksheet named 'Pipeline'
    - Have a named range Pipeline!name
    - Have a named range Pipeline!pipe_table with a header row and the following columns:
        - Pipe Name: The name of the pipesection or pump
            - If this is a pipesection, any valid string not containing the word 'pump'
            - If a pump, the name of the tab defining the pump (for pumps the other columns are ignored)
        - Diameter: The pipe diameter in m
        - Length: The pipe length in m
        - Total K: The total of fitting k-factors for this section of pipe
        - Elev Change: The change in elevation for this section of pipe, in m
- One worksheet named 'Slurry'
    - Have named ranges Slurry!['name', 'Cv', 'd_15', 'd_50', 'd_85', 'fluid', 'pipe_dia', 'rhoi', 'rhos']
    - d_15, d_50, d_85 are diameters in mm
    - pipe_dia is in m
    - fluid is 'salt' or 'fresh'
    - rhos is the solids density in ton/m3
    - rhoi is the insitu density in ton/m3
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

from DHLLDV.DriverObj import Driver
from DHLLDV.PumpObj import Pump
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.SlurryObj import Slurry
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
    cell_range = next(my_range.destinations)[1]  # returns a generator of (worksheet title, cell range) tuples
    rows = wb[sheet_name][cell_range]
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


def load_pipeline_from_workbook(wb: openpyxl.Workbook):
    """Create a pipeline object from a workbook
    wb: The workbook to load
    """
    pump_sheets = {}
    driver_sheets = {}
    for ws_name in wb.sheetnames:
        sheet_id = wb.sheetnames.index(ws_name)  # The id / index of a worksheet
        if 'pipeline' in ws_name.lower():
            pipeline_name = get_range_value(wb, sheet_id, 'name')
            pipesheet_id = sheet_id
        elif 'pump' in ws_name.lower():
            pump_sheets[ws_name.lower().removesuffix('pump')] = sheet_id
        elif 'driver' in ws_name.lower():
            driver_sheets[ws_name.lower().removesuffix('driver')] = sheet_id
        elif 'slurry' in ws_name.lower():
            slurry = load_slurry_from_workbook(wb, sheet_id)
        else:
            ...
    pumps = {}
    for pump_name in pump_sheets:
        pumps[pump_name] = load_pump_from_worksheet(wb, pump_sheets[pump_name], driver_sheets.get(pump_name))

    my_range = wb.defined_names.get('pipe_table', pipesheet_id)
    sheet_name = wb.sheetnames[pipesheet_id]
    name_col = None
    dia_col = None
    len_col = None
    k_col = None
    dz_col = None
    cell_range = next(my_range.destinations)[1]  # returns a generator of (worksheet title, cell range) tuples
    rows = wb[sheet_name][cell_range]
    pipes = []
    for row in rows:
        vals = [c.value for c in row]
        if name_col is None:  # Assume the first row is a header
            name_col = next(i for i, c in enumerate(vals) if 'name' in c.lower())
            dia_col = next(i for i, c in enumerate(vals) if 'dia' in c.lower())
            len_col = next(i for i, c in enumerate(vals) if 'length' in c.lower())
            k_col = next(i for i, c in enumerate(vals) if all(['total' in c.lower(),
                                                              'k' in c.lower()]))
            dz_col = next(i for i, c in enumerate(vals) if all(['elev' in c.lower(),
                                                              'change' in c.lower()]))
        elif 'pump' in vals[name_col].lower():
            pump_name = vals[name_col].lower().removesuffix('pump')
            pipes.append(pumps[pump_name])
        else:
            pipes.append(Pipe(name=vals[name_col],
                              diameter=float(vals[dia_col]),
                              length=float(vals[len_col]),
                              total_K=float(vals[k_col]),
                              elev_change=float(vals[dz_col])))
    return Pipeline(name=pipeline_name, slurry=slurry)


def load_slurry_from_workbook(wb: openpyxl.workbook, sheet_id: int):
    """Load the slurry defined on the 'Slurry' tab of the given workbook

    wb: The workbook with the data
    sheet_id: The id of the Slurry tab"""
    single_values = {'name': str,
                     'pipe_dia': float,
                     'd_15': float,
                     'd_50': float,
                     'd_85': float,
                     'fluid': str,
                     'Cv': float,
                     'rhos': float,
                     'rhoi': float
                     }

    params = dict([(k, v(get_range_value(wb, sheet_id, k))) for k, v in single_values.items()])
    s = Slurry(name=params['name'],
               Dp=params['pipe_dia'],
               D50=params['d_50']/1000,
               fluid=params['fluid'],
               Cv=params['Cv'],
               )
    s.generate_GSD(d15_ratio=params['d_50']/params['d_15'],
                   d85_ratio=params['d_85']/params['d_50'])
    s.rhos = params['rhos']
    s.rhoi = params['rhoi']
    return s


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
            ret_val = load_pipeline_from_workbook(wb)
        elif 'pump' in ws_name.lower():
            input_type = 'pump'
            pumps[ws_name.lower().removesuffix('pump')] = sheet_id
        elif 'driver' in ws_name.lower():
            input_type = 'driver'
            drivers[ws_name.lower().removesuffix('driver')] = sheet_id
        elif 'slurry'in ws_name.lower():
            input_type = 'slurry'
            ret_val = load_slurry_from_workbook(wb, sheet_id)
        else:
            input_type = ws_name
        print(f'{sheet_id} {input_type}: {wb[ws_name]}')        # Accessing individual worksheets
        print(wb.defined_names.localnames(sheet_id))  # Range names in a worksheet
        print(ret_val)

