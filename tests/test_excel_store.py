"""test_excel_store - Tests of store_pump_excel in the Viewer

Added by R. Ramsdell 2024-08-28
"""
import os
import unittest

import openpyxl

from DHLLDV_viewer import load_pump_excel, store_pump_excel


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """Load the example file into memory"""
        self.input_fname = "tests/Example_excel_input.xlsx"
        self.output_fname = None  # This is a placeholder for the real name, which will be created by the store_to_excel
        self.input_wb = openpyxl.load_workbook(filename=self.input_fname, data_only=True)
        self.in_pipeline = load_pump_excel.load_pipeline_from_workbook(self.input_wb)
        self.output_fname = store_pump_excel.store_to_excel(self.in_pipeline, path='tests')
        self.output_wb = openpyxl.load_workbook(filename=self.output_fname, data_only=True)
        self.out_pipeline = load_pump_excel.load_pipeline_from_workbook(self.output_wb)

    def tearDown(self):
        """Delete the newly-created output file"""
        os.remove(self.output_fname)

    def test_roundtrip_objects(self):
        """Test storing then loading the pipeline and pump objects correctly"""
        pipeline = self.out_pipeline
        self.assertEqual('UWP 34x34x60 @ 300RPM', pipeline.pumps[0].name)
        self.assertEqual('0.864x0.864x2.134m Pump at 315 RPM', pipeline.pumps[1].name)
        self.assertEqual('Entrance', pipeline.pipesections[0].name)
        self.assertEqual('UWP 34x34x60 @ 300RPM', pipeline.pipesections[2].name)
        self.assertEqual('Shore Line', pipeline.pipesections[-1].name)

    def test_load_calculations(self):
        """Test that the pipeline calculations are correct for a stored then loaded pipeline"""
        pipeline = self.out_pipeline

        flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
        self.assertAlmostEqual(3.4017658516096114, pipeline.find_operating_point(flow_list))

        flow = 4.0
        for param, expected, actual in zip(('System head slurry', 'System head fluid', 'Pump head slurry', 'Pump head fluid'),
                                           (155.83833315609024, 147.87084371417842, 101.75436068325409, 95.93219789540075),
                                           pipeline.calc_system_head(flow)):
            with self.subTest(msg=param):
                self.assertAlmostEqual(expected, actual, 5)
        for param, expected, actual in zip(('Flow', 'Pump Head', 'Pump Power', 'Pump Speed'),
                                           (4.0, 74.32723942350866, 3728.499999999634, 4.811435751810117),
                                           pipeline.pumps[1].point(flow)):
            with self.subTest(msg=param):
                self.assertAlmostEqual(expected, actual, 5)


if __name__ == '__main__':
    unittest.main()
