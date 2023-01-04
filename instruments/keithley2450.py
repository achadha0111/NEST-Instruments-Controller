import datetime
import time

import pandas as pd

from keithley2450api import keithley
from vdpcomputation import vdp
from pymeasure.experiment import (unique_filename, Experiment, Results, Worker)
from os.path import exists
from os import makedirs

import streamlit as st

# X1-X2-X3-X4_{N,S}: X1-X2 are the FORCE (CURRENT) HI and LO respectively.
# X3-X4 are SENSE (VOLTAGE) HI and LO respectively.
# Trailing letter is for direction of magnetic field in Hall Measurements
configurations = [
    "4312",
    "3421",
    "3241",
    "2314",
    "1243",
    "2134",
    "4132",
    "1423",
    "1324_N",
    "3142_N",
    "2413_N",
    "4231_N",
    "1324_S",
    "3142_S",
    "2413_S",
    "4231_S"
]


# Calculation based on:
# Melios, C. et al. Towards standardisation of contact and
# contactless electrical measurements of CVD graphene at the macro-, micro- and nano-scale.
# Sci Rep 10, 3223 (2020).
def process_data(mtype, pconfigs, sample, magneticfield):
    vdp_data = vdp.VDPComputation(pconfigs, sample)
    with st.spinner("Processing"):
        if mtype == "Hall Measurement":
            mobility_result = vdp_data.compute_hall_mobility(magneticfield)
            st.write(f"Hall mobility for {sample} calculated "
                     f"to be {mobility_result['mu']} cm^2 v^{-1}s^{-1}."
                     f"Corresponding sheet resistance is {mobility_result['Rs']}."
                     f"Vertical to Horizontal "
                     f"Resistance ratio was {mobility_result['r_ratio']}.")
        else:
            rs_result = vdp_data.compute_sheet_resistance()
            st.write(f"Sheet resistance for {sample} is {rs_result['Rs']}."
                     f"Vertical to Horizontal "
                     f"Resistance ratio was {rs_result['r_ratio']}")


def execute_measurement(sample, sweep, averages, min_current, max_current, port, config):
    data_filename = unique_filename('../PhD/Data Analysis/2023/data/hall-measurement/{0}'.format(sample), prefix=config,
                                    datetimeformat="", suffix="")
    # file_version_number = data_filename.split("_")[-1].split(".")[0]

    if not exists("../PhD/Data Analysis/2023/data/hall-measurement/{0}".format(sample)):
        makedirs("../PhD/Data Analysis/2023/data/hall-measurement/{0}".format(sample))
    procedure = keithley.HallProcedure(data_points=sweep, averages=averages,
                                       max_current=max_current, min_current=min_current, port=port)
    results = Results(procedure, data_filename)
    worker = Worker(results)
    worker.start()
    worker.join(timeout=300)
    data = pd.read_csv(data_filename, skiprows=3)
    st.text("Collected Data")
    st.table(data)
    st.line_chart(data, x="Current (A)", y="Voltage (V)")


def display_controls():
    st.title("Keithley 2450")

    default_sample_name = f"Sample {datetime.datetime.now().strftime('%d/%m/%Y')}"
    measurement_setup = st.form("Setup Instrument")
    instrument_port = measurement_setup.text_input("Instrument Connection Port",
                                                   value="USB0::0x05E6::0x2450::04365678::INSTR")
    sample_name = measurement_setup.text_input("Sample Name", placeholder=default_sample_name)
    sweep = measurement_setup.number_input("Sweep Steps", min_value=1, max_value=100)
    measurement_setup.warning("For Hall Effect Measurements, leave this to be 1")
    averages = measurement_setup.number_input("Averages (number of readings per step)",
                                              value=10, min_value=1, max_value=100)
    min_current = measurement_setup.number_input("Min current (mA)", min_value=0.1, max_value=1000.0)
    max_current = measurement_setup.number_input("Max current (mA)",
                                                 min_value=0.1, value=1.0, max_value=1000.0)
    magnetic_field = measurement_setup.number_input("Applied Magnetic Field (T)", min_value=0, max_value=2)
    measurement_setup.info("Do not change magnetic field if computing sheet resistance")
    probe_configuration = measurement_setup.selectbox("Select probe configuration", configurations)
    start_measurement_button = measurement_setup.form_submit_button("Start Measurement")
    if start_measurement_button:
        st.write(f"Measuring configuration {probe_configuration}")
        execute_measurement(sample_name, sweep,
                            averages, min_current, max_current,
                            instrument_port, probe_configuration)

    computation_form = st.form("Data processing form")
    computation_form.title(f"Process Data")
    mType = computation_form.radio("Measurement", ["Hall Measurement", "4-point vDP Sheet Resistance"])
    process_data_button = computation_form.form_submit_button("Process Data")
    if process_data_button:
        process_data(mType, configurations, sample_name, magnetic_field)
