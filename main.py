import streamlit as st
from instruments import ils, keithley2450

st.sidebar.write("NEST Instrument Controller")
available_instruments = {"Keithley 2450": keithley2450, "Indoor Light Simulator": ils}
instrument_selection = st.sidebar.selectbox("Instrument:", ["Keithley 2450", "Indoor Light Simulator"])
available_instruments[instrument_selection].display_controls()



