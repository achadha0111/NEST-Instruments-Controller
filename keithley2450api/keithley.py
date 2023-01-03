import time
import math
import numpy as np

from pymeasure.experiment import (Experiment, Results, Worker)
from pymeasure.instruments.keithley import Keithley2450
from pymeasure.experiment import (Procedure, IntegerParameter, FloatParameter, unique_filename, Results)


class HallProcedure(Procedure):
    # data_points = IntegerParameter('Data Points', default=5)
    # averages = IntegerParameter('Averages', default=5)
    # max_current = FloatParameter('Max Current', units='A', default=1e-3)
    # min_current = FloatParameter('Min Current', units='A', default=1e-4)

    DATA_COLUMNS = ["Current (A)", "Voltage (V)", "Resistance (Ω)", "Instrument Uncertainty"]

    def __init__(self, data_points, averages, max_current, min_current, port):
        super(HallProcedure, self).__init__()
        self.port = port
        self.data_points = data_points
        self.averages = averages
        self.max_current = max_current/1000.0
        self.min_current = min_current/1000.0

    def startup(self):
        self.sourcemeter = Keithley2450(self.port)
        self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        # https://github.com/pymeasure/pymeasure/issues/597
        self.sourcemeter.apply_current()
        self.sourcemeter.compliance_voltage = 2.1
        self.sourcemeter.measure_voltage()
        self.sourcemeter.write(":SENS:VOLT:RSENSE 4")
        self.sourcemeter.enable_source()
        time.sleep(2)

    ''' Each tuple represents (offset (V or A), % of reading)'''
    @staticmethod
    def get_instrument_accuracy(acc_type, measurement):
        acc_table = {
            "mVoltage": {
                -8: (150e-6, 0.001),
                -7: (150e-6, 0.001),
                -6: (150e-6, 0.001),
                -5: (150e-6, 0.001),
                -4: (150e-6, 0.001),
                -3: (150e-6, 0.001),
                -2: (150e-6, 0.001),
                -1: (200e-6, 0.00012),
                0: (300e-6, 0.00012),
                1: (1e-3, 0.00015),
                2: (10e-3, 0.00015),
            },
            "sCurrent": {
                -8: (100e-12, 0.001),
                -7: (150e-12, 0.0006),
                -6: (400e-12, 0.00025),
                -5: (1.5e-9, 0.00025),
                -4: (15e-9, 0.00020),
                -3: (150e-9, 0.00020),
                -2: (1.5e-6, 0.00020),

            }
        }

        return acc_table[acc_type][math.floor(math.log10(abs(measurement)))]

    ''' Calculate the error due to instrument accuracy. This makes use of the Keithley 2450
    accuracy table '''

    def calculate_ins_acc(self, source_current, measured_voltage, resistance):
        v_range = self.get_instrument_accuracy("mVoltage", measured_voltage)
        error_v = (measured_voltage * v_range[1]) + v_range[0]
        i_range = self.get_instrument_accuracy("sCurrent", source_current)
        error_i = (source_current * i_range[1]) + i_range[0]
        abs_err_r = (error_v + error_i)

        return abs_err_r

    def execute(self):
        currents = np.linspace(
            self.min_current,
            self.max_current,
            num=self.data_points)

        for current in currents:
            avg_volt = 0
            avg_res = 0
            avg_err_res = 0
            self.sourcemeter.source_current = current
            measured_current = self.sourcemeter.source_current
            for reading in range(self.averages):
                voltage = self.sourcemeter.voltage
                resistance = voltage / measured_current
                type_b_error = self.calculate_ins_acc(measured_current, voltage, resistance)
                avg_err_res += type_b_error
                avg_volt += voltage
                avg_res += resistance
                time.sleep(0.1)
                if self.should_stop():
                    break

            self.emit('results', {
                'Current (A)': measured_current,
                'Voltage (V)': avg_volt / self.averages,
                'Resistance (Ω)': avg_res / self.averages,
                "Instrument Uncertainty": avg_err_res / self.averages
            })

    def shutdown(self):
        self.sourcemeter.shutdown()