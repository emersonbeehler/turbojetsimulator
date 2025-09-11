import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def calculate_stages(values):
    # Unpack values dictionary
    u = values["Airspeed (km/h):"]
    z = values["Altitude (m):"]
    A = values["Inlet Area (m^2):"]
    PRc = values["Compressor Pressure Ratio:"]
    T_max = values["Turbine Inlet Temperature (K):"]
    eta_c = values["Compressor Isentropic Efficiency (%):"]
    eta_t = values["Turbine Isentropic Efficiency (%):"]
    eta_comb = values["Fuel Combustion Efficiency (%):"]
    fueltype = values["Fuel Type:"]
    
    # Fix efficiencies
    eta_c = eta_c / 100
    eta_t = eta_t / 100
    eta_comb = eta_comb / 100

    # Initialize static variables
    gamma = 1.4
    cp = 1005 # J/kg/K
    R = 287.0

    # Set fuel LHV. Units: MJ/kg
    match fueltype:
        case "JP-8 (military standard)":
            LHV = 42.8
        case "Jet-A (civilian standard)":
            LHV = 43.2

    # Convert airspeed from km/h to m/s
    u = u / 3.6

    # -- Stage by stage calculations -- 
    # Static atmospheric conditions
    T_0 = 288.15 - (0.0065 * z) # K
    P_0 = (101.325) * ((T_0 / 288.15) ** 5.256) # kPa
    rho = (P_0 * 1000)/ (R * T_0) # kg/m^3
    mdot = rho * u * A # mass flow (kg/s)

    # Inlet (0 -> 1)
    P_1 = P_0 # static pressure
    T_1 = T_0 # static temperature
    
    # Diffuser (1 -> 2) (converts KE -> stagnation pressure + temperature)
    ke_0 = 0.5 * (u ** 2) # specific KE (J/kg)
    Tt_2 = T_1 + (ke_0 / cp)
    Pt_2 = P_1 * (Tt_2 / T_1) ** (gamma / (gamma - 1))

    # Compressor (2 -> 3)
    Pt_3 = PRc * Pt_2
    Tt_3s = Tt_2 * (PRc ** ((gamma - 1) / gamma)) # isentropic
    Tt_3 = Tt_2 + ((Tt_3s - Tt_2) / eta_c) # actual w/efficiency

    # Combustion (3 -> 4)
    Pt_4 = Pt_3 # assume no pressure loss
    Tt_4 = T_max # assume temperature brought to max TIT

    # Turbine (4 -> 5)
    Tt_5s = Tt_4 - (Tt_3 - Tt_2) # Ideal turbine extracts enough work to drive compressor
    Tt_5 = Tt_4 - ((Tt_4 - Tt_5s) / eta_t)
    Pt_5 = Pt_4 * ((Tt_5s / Tt_4) ** (gamma / (gamma - 1)))

    # Nozzle (5 -> e)
    T_e = Tt_5 * ((P_0 / Pt_5) ** ((gamma - 1) / gamma))
    v = np.sqrt(2 * cp * (Tt_5 - T_e))

    # -- Performance Metrics --
    # Thrust
    F = mdot * (v - u)

    # Required Fuel Mass Flow Rate (kg/s)
    mdot_f = (mdot * cp * (Tt_4 - Tt_3)) / (eta_comb * LHV * 1000000) # converted LHV from MJ to J

    # Specific Fuel Consumption (g/s/kN)
    SFC = mdot_f / F * 1000000

    # Efficiency Calculations
    eta_th = (1 - (T_0 / Tt_3))
    eta_prop = (2 / (1 + (v / u)))
    eta_overall = eta_th * eta_prop

    # Normalize efficiencies
    eta_th = eta_th * 100
    eta_prop = eta_prop * 100
    eta_overall = eta_overall * 100

    results = {
        "T_0" : T_0, "P_0" : P_0, "T_1" : T_1, "P_1" : P_1, "T_2" : Tt_2, "P_2" : Pt_2,
        "T_3" : Tt_3, "P_3" : Pt_3, "T_4" : Tt_4, "P_4" : Pt_4, "T_5" : Tt_5, "P_5" : Pt_5,
        "T_e" : T_e, "v" : v, "F" : F, "mdot_f" : mdot_f, "SFC" : SFC, "eta_th" : eta_th,
        "eta_prop" : eta_prop, "eta_overall" : eta_overall,
    }

    values.update(results)
    return values


def main():
    # Get data
    values = {}
    for text, entry in entries.items():
        x = entry.get().strip()

        if not x:
            messagebox.showerror("Input Error", f"Error. Input all parameters before calculating.")
            return
        try:
            values[text] = float(x)
        except ValueError:
            if x == "Jet-A (civilian standard)" or "JP-8 (military standard)":
                values[text] = x
            else:
                messagebox.showerror("Input Error", f"Error. All parameters must be a number")
                return

    # Calculate stages
    results = calculate_stages(values)

    # Update GUI
    exhaustvelocity_label.config(text=f"Exhaust Velocity: {results['v']:.2f} m/s")
    thrust_label.config(text=f"Thrust: {results['F']:.2f} N")
    mdot_f_label.config(text=f"Required Mass Flow Rate: {results['mdot_f']:.2f} kg/s")
    SFC_label.config(text=f"Specific Fuel Consumption: {results['SFC']:.2f} g/kN/s")
    eta_th_label.config(text=f"Thermal Efficiency: {results['eta_th']:.2f} %")
    eta_prop_label.config(text=f"Propulsive Efficiency: {results['eta_prop']:.2f} %")
    eta_overall_label.config(text=f"Overall Efficiency: {results['eta_overall']:.2f} %")

    ## Update graphs
    tplot.clear()
    pplot.clear()

    # Update Temperature Plot
    t_y = [results["T_0"], results["T_1"], results["T_2"], results["T_3"], results["T_4"], results["T_5"], results["T_e"]]
    tplot.plot(range(len(t_y)), t_y)
    tplot.set_title("Temperatures Across Engine")
    tplot.set_xlabel("Stages of Engine")
    tplot.set_ylabel("Temperature (K)")

    # Update Pressure Plot
    p_y = [results["P_0"], results["P_1"], results["P_2"], results["P_3"], results["P_4"], results["P_5"], results["P_0"]]
    pplot.plot(range(len(p_y)), p_y)
    pplot.set_title("Pressures Across Engine")
    pplot.set_xlabel("Stages of Engine")
    pplot.set_ylabel("Pressure (kPa)")

    fig.tight_layout(pad=2.0)
    canvas.draw()

    

### Create main GUI
root = tk.Tk()
root.geometry("800x600")
root.title ("Turbojet Simulator")

# Configure grid layout
frame = tk.Frame(root)
frame.pack()
frame.grid_rowconfigure(0, weight=1)

## Take input parameters
input = tk.LabelFrame(frame, text="Input Turbojet Parameters")
input.grid(row=0, column = 0, sticky='nsew')

fields = {
    "Airspeed (km/h):" : tk.Entry,
    "Altitude (m):" : tk.Entry,
    "Inlet Area (m^2):" : tk.Entry,
    "Compressor Pressure Ratio:" : tk.Entry,
    "Turbine Inlet Temperature (K):" : tk.Entry,
    "Compressor Isentropic Efficiency (%):" : tk.Entry,
    "Turbine Isentropic Efficiency (%):" : tk.Entry,
    "Fuel Combustion Efficiency (%):" : tk.Entry,
    "Fuel Type:" : ttk.Combobox,
}

entries = {}

# Create each entry field iteritively
for i, (text, type) in enumerate(fields.items()):
    tk.Label(input, text=text).grid(row=i, column=0, padx=10, pady=5)

    if type == tk.Entry:
        entry = tk.Entry(input)
        entry.grid(row=i, column=1, padx=10, pady=5)
    elif type == ttk.Combobox:
        entry = ttk.Combobox(input, values=["JP-8 (military standard)", "Jet-A (civilian standard)"], state="readonly")
        entry.current(0)
        entry.grid(row=i, column=1, padx=10, pady=5)
        
    entries[text] = entry

# Button
calculate_button = tk.Button(input, text="Calculate", command = main)
calculate_button.grid(row=9, column=0, columnspan=2, pady=10)

## Display output metrics
output = tk.LabelFrame(frame, text="Performance Metrics")
output.grid(row=0, column=1, sticky='nsew')

# Exhaust Velocity
exhaustvelocity_label = tk.Label(output, text="Exhaust Velocity: N/A")
exhaustvelocity_label.grid(row=0, column=0, padx=10, pady=5)

# Thrust
thrust_label = tk.Label(output, text="Thrust: N/A")
thrust_label.grid(row=1, column=0, padx=10, pady=5)

# Required fuel mass flow rate
mdot_f_label = tk.Label(output, text="Required Mass Flow Rate: N/A")
mdot_f_label.grid(row=2, column=0, padx=10, pady=5)

# SFC
SFC_label = tk.Label(output, text="Specific Fuel Consumption: N/A")
SFC_label.grid(row=3, column=0, padx=10, pady=5)

# Thermal Efficiency
eta_th_label = tk.Label(output, text="Thermal Efficiency: N/A")
eta_th_label.grid(row=4, column=0, padx=10, pady=5)

# Propulsive Efficiency
eta_prop_label = tk.Label(output, text="Propulsive Efficiency: N/A")
eta_prop_label.grid(row=5, column=0, padx=10, pady=5)

# Overall Efficiency
eta_overall_label = tk.Label(output, text="Overall Efficiency: N/A")
eta_overall_label.grid(row=6, column=0, padx=10, pady=5)

## Create blank graphs
fig = Figure(figsize=(6, 4), dpi=100)

# Temperature plot
tplot = fig.add_subplot(2, 1, 1)
tplot.plot([], [])
tplot.set_title("Temperatures Across Engine")
tplot.set_xlabel("Stages of Engine")
tplot.set_ylabel("Temperature (K)")

# Pressure plot
pplot = fig.add_subplot(2, 1, 2)
pplot.plot([], [])
pplot.set_title("Pressures Across Engine")
pplot.set_xlabel("Stages of Engine")
pplot.set_ylabel("Pressure (kPa)")

fig.tight_layout(pad=2.0)
canvas = FigureCanvasTkAgg(fig, master=output)
canvas.draw()
canvas.get_tk_widget().grid(row=7, column=0,)


root.mainloop()