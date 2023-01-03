import datetime
import time

import pandas as pd

from keithley2450api import keithley
from pymeasure.experiment import (unique_filename, Experiment, Results, Worker)
from os.path import exists
from os import makedirs

import streamlit as st

configurations = [
    "1243_off",
    "4312_off",
    "1423_off",
    "2314_off",
    "1243_on",
    "4312_on",
    "1423_on",
    "2314_on",
]

def process_data(mType, configurations, sample):
    st.write(sample)


def execute_measurement(sample, sweep, averages, min_current, max_current, magnetic_field, port, config):
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
    worker.join(timeout=300)  # wait at most 1 hr (3600 sec)
    data = pd.read_csv(data_filename, skiprows=3)
    st.text("Collected Data")
    st.table(data)
    st.line_chart(data, x="Current (A)", y="Voltage (V)")



def display_controls():
    st.title("Keithley 2450")

    default_sample_name = f"Sample {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    measurement_setup = st.form("Setup Instrument")
    instrument_port = measurement_setup.text_input("Instrument Connection Port",
                                                   value="USB0::0x05E6::0x2450::04365678::INSTR")
    sample_name = measurement_setup.text_input("Sample Name", value=default_sample_name)
    sweep = measurement_setup.number_input("Sweep Steps", min_value=1, max_value=100)
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
                            magnetic_field, instrument_port, probe_configuration)

    computation_form = st.form("Data processing form")
    computation_form.title(f"Process Data")
    mType = computation_form.radio("Measurement", ["Hall Measurement", "4-point vDP Sheet Resistance"])
    process_data_button = computation_form.form_submit_button("Process Data")
    if process_data_button:
        process_data(mType, configurations, sample_name)


