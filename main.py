import streamlit as st
from huebridgeapi import connection

st.title("Indoor Light Simulator")

st.write("This interface controls a GU10 Hue Bulb. By modifying brightness and colour temperature, various indoor"
         " lighting conditions can be simulated.")

bridge_form = st.form("Hue Control")
hue_bridge_address = bridge_form.text_input("Enter IP address of Hue Bridge")
connect_button = bridge_form.form_submit_button("Connect")

if connect_button:
    bridge_connection = connection.HueBridgeConnection(hue_bridge_address, "")
    connect = bridge_connection.establish_connection()

    flow_opts = {
        "Pending": connect["message"],
        "Failed": connect["message"],
        "Success": bridge_connection.display_parameters_form
    }

    flow_opts[connect["status"]]()

