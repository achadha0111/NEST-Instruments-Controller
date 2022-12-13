import requests
import streamlit as st
import numpy as np


class HueBridgeConnection:
    def __init__(self, ip_address, hue_user_id):
        self.ip_address = ip_address
        self.hue_user_id = hue_user_id
        self.base_url = f"https://{self.ip_address}/api"

    """
        Connect to hue bridge using API. On first successful connect,
        this function will return a "Press link button message".
        On the subsequent request, it will return a user id
        for subsequent requests.
        
        :param hue_bridge_address
        :returns streamlit message
    """

    def establish_connection(self):
        user = "Streamlit-Hue-Controller"
        conn_result = requests.post(self.base_url, data={"devicetype": user})
        if "error" in conn_result[0] and conn_result[0]["error"]["type"] == 101:
            st.warning('This is a warning', icon="⚠️")
            result = {"status": "Pending",
                      "message": st.warning("Press link button on Hue Bridge and try connect again", icon="⚠️")}
            return result
        elif "success" in conn_result[0]:
            self.hue_user_id = conn_result[0]["success"]["username"]
            result = {"status": "Success", "message": st.success("Connection succeeded", icon="✅")}
            return result

        return {"status": "Success",
                "message": st.error("Connection failed. Please check your network and try again", icon="🚨")}

    def display_parameters_form(self):
        with st.form("Connection_Parameters"):
            light_brightness = st.select_slider("Set Brightness", options=range(0, 255, 1), value=[0, 254])
            light_ct = st.select_slider("Set Temperature", options=range(153, 455, 1), value=[153, 454])

            trigger_button = st.form_submit_button("Set Light State")
            if trigger_button:
                self.set_light_parameters(light_brightness, light_ct)

    def set_light_parameters(self, bri, ct):
        post_params = requests.post(self.base_url + "/lights/1/state", data={"on": True, "ct": ct, "bri": bri})

    def turnoff_light(self):
        post_params = requests.post(self.base_url + "/lights/1/state", data={"on": False})
