import datetime
import pandas as pd
import streamlit as st
import serial
import time


class ArduinoConnection:
    def __init__(self):
        self.port = ""
        self.baud_rate = 9600

    def display_blink_form(self):
        st.title("Shutter Control")
        st.warning("Currently, blinks received by arduino are N-1. Needs to be investigated!", icon="⚠️")
        num_blinks = st.number_input("Select number of blinks", min_value=1, max_value=100, step=1)
        uniform = st.checkbox("Uniform (duration and interval for first blink is uniformly applied)")
        arduino_port = st.text_input("Enter arduino port name")
        duration_col, interval_col = st.columns(2)
        with duration_col:
            blink_durations = [st.number_input(f"Blink {i+1} "
                                               f"Duration (ms)", min_value=0, max_value=1000, key=f"{i}_duration") for i in
                               range(num_blinks)]
            setup_arduino_button = st.button("Setup Shutter")
        with interval_col:
            post_blink_intervals = [st.number_input(f"Post Blink {i+1} Interval (ms)",
                                                    min_value=10, max_value=1000, key=f"{i}_interval") for i in range(num_blinks)]
            save_parameters = st.button("Save parameters")

        if uniform:
            uniform_duration, uniform_interval = blink_durations[0], post_blink_intervals[0]
            blink_durations = [uniform_duration for _ in blink_durations]
            post_blink_intervals = [uniform_interval for _ in post_blink_intervals]

        if save_parameters:
            self.save_test_parameters(blink_durations, post_blink_intervals)

        # self.update_square_wave_preview(blink_durations, post_blink_intervals)

        if setup_arduino_button:
            st.write(f"Blink durations: {blink_durations}")
            self.setup_arduino(blink_durations, post_blink_intervals, arduino_port)
            self.save_test_parameters(blink_durations, post_blink_intervals)

    # def update_square_wave_preview(self, blink_durations, post_blink_intervals):
    #     chart_data = pd.DataFrame(columns=["Time", "Signal"])
    #     st.line_chart(chart_data)
    def setup_arduino(self, blink_duration, post_blink_intervals, port):
        blinks = len(blink_duration)
        device = serial.Serial(port, baudrate=115200)
        time.sleep(1)
        progress_bar = st.progress(0)
        for blink in range(blinks):
            device.write(b'H')
            time.sleep(blink_duration[blink]/1000)
            device.write(b'L')
            time.sleep(post_blink_intervals[blink]/1000)
            progress_bar.progress(blink/(blinks-1))

    def save_test_parameters(self, durations, intervals):
        df = pd.DataFrame({"blink_length": durations, "interval": intervals})
        file_name = "Blink Parameters_"+ (datetime.datetime.now()).strftime("%m-%d-%Y, %H:%M:%S")
        df.to_csv(f"{file_name}.csv")


