import streamlit as st
from huebridgeapi import connection as hbc
from arduinoapi import connection as ac

st.title("Indoor Light Simulator")

st.write("This interface controls a GU10 Hue Bulb. By modifying brightness and colour temperature, various indoor"
         " lighting conditions can be simulated.")

# bridge_form = st.form("Hue Control")
# hue_bridge_address = bridge_form.text_input("Enter IP address of Hue Bridge")
# connect_button = bridge_form.form_submit_button("Connect")
# bridge_connection = hbc.HueBridgeConnection(hue_bridge_address, "")
arduino_connection = ac.ArduinoConnection()

bridge_column, light_column = st.columns(2)

with bridge_column:
    bridge_form = st.form("Hue Control")
    bridge_form.title("Bridge Connect")
    hue_bridge_address = bridge_form.text_input("Enter IP address of Hue Bridge")
    connect_button = bridge_form.form_submit_button("Connect")
    bridge_connection = hbc.HueBridgeConnection(hue_bridge_address)
    if connect_button:
        bridge_connection.establish_connection()
with light_column:
    bridge_connection.display_parameters_form()

arduino_connection.display_blink_form()

