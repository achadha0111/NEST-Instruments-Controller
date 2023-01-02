import requests
import streamlit as st
import numpy as np


class HueBridgeConnection:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.hue_user_id = None
        self.base_url = f"http://{self.ip_address}/api"

    """
        Connect to hue bridge using API. On first successful connect,
        this function will return a "Press link button message".
        On the subsequent request, it will return a user id
        for subsequent requests.
        
        :param hue_bridge_address
        :returns streamlit message
    """

    def establish_connection(self):
        user = "StreamlitHueController"
        conn_result = requests.post(self.base_url, json={"devicetype": user}).json()
        if "error" in conn_result[0] and conn_result[0]["error"]["type"] == 101:
            result = {"status": "Pending",
                      "message": st.warning("Press link button on Hue Bridge and try again", icon="⚠️")}
            return result
        elif "success" in conn_result[0]:
            self.hue_user_id = conn_result[0]["success"]["username"]
            self.store_in_state(self.hue_user_id)
            result = {"status": "Success", "message": st.success("Connection succeeded", icon="✅")}
            return result

        return {"status": "Error",
                "message": st.error("Connection failed. Please check your network and try again", icon="🚨")}

    def display_parameters_form(self):
        with st.form("Connection_Parameters"):
            st.title("Light Control")
            trigger_button = st.form_submit_button("Set Light State")
            light_brightness = st.select_slider("Set Brightness", options=range(0, 255, 1), value=[0, 254])
            light_ct = st.select_slider("Set Temperature", options=range(2200, 6501, 1), value=[2200, 6500])
            light_off_button = st.form_submit_button("Turn Light Off")
            if trigger_button:
                self.set_light_parameters(light_brightness, light_ct)

            if light_off_button:
                self.turnoff_light()

    def set_light_parameters(self, bri, ct):
        request_url = self.base_url + f"/{st.session_state['current_user']}/lights/1/state"
        requests.put(request_url, json={"on": True, "ct": ct[1]/14.31, "bri": bri[1]})

    def turnoff_light(self):
        requests.put(self.base_url + f"/{st.session_state['current_user']}/lights/1/state", json={"on": False})

    def store_in_state(self, userid):
        if "current_user" not in st.session_state:
            st.session_state["current_user"] = userid
