import pandas as pd
import math

class VDPComputation:
    def __init__(self, configurations, sample):
        self.configurations = configurations
        self.sample_name = sample

    def calculate_rs(self, df):
        r_horz = df[df["Configuration"].isin([4312, 3421, 1243, 2134])]["Resistance"].mean()
        r_vert = df[df["Configuration"].isin([3241, 2314, 4132, 1423])]["Resistance"].mean()
        r_ratio = r_vert/ r_horz
        rs = (math.pi / math.log(2)) * ((r_vert + r_horz) / 2)
        return {"r_ratio": r_ratio, "Rs": rs}

    def compute_sheet_resistance(self):
        measurement_df = self.fetch_data(self.sample_name, "Rs")
        return self.calculate_rs(measurement_df)

    def compute_hall_mobility(self, fieldstrength):
        measurement_df = self.fetch_data(self.sample_name, "Hall")
        rs_data = self.calculate_rs(measurement_df)
        return {"mu": (measurement_df["Hall Voltage"].sum())/(8*measurement_df["Current (A)"]*fieldstrength*rs_data["Rs"]),
                "r_ratio": rs_data["r_ratio"],
                "Rs": rs_data["Rs"]}

    @staticmethod
    def fetch_data(self, sample, datatype):
        data_directory = f'../PhD/Data Analysis/2023/hall-measurement/{sample}'
        # df = pd.DataFrame(columns=["Configuration", "Resistance (Ω)"])
        data = []
        for config_name in self.configurations[0:9]:
            config_df = pd.read_csv(f"{data_directory}/{config_name}.csv", skiprows=3)
            data.append({"Resistance (Ω)": config_df["Resistance (Ω)"].mean(),
                         "Configuration": config_name})
        if datatype == "Hall":
            for config_name in self.configurations[9:13]:
                config_df_n = pd.read_csv(f"{data_directory}/{config_name}.csv", skiprows=3)
                config_df_s = pd.read_csv(f"{data_directory}/{config_name.replace('_N', '_S')}.csv", skiprows=3)
                data.append({"Configuration": config_name,
                             "Hall Voltage (V)": config_df_s["Voltage (V)"] - config_df_n["Voltage (V)"],
                            "Current (A)": (config_df_s["Current (A)"] + config_df_n["Current (A)"])/2})
        df = pd.DataFrame.from_records(data=data)
        return df
