# Turbojet Engine Performance Simulator

Python app that uses user-defined parameters to calculate the performance of a turbojet engine using the ideal Brayton cycle.
Outputs key performance metrics (e.g. thrust), and generates temperature and pressure graphs for each stage in the cycle.

## Features
- Calculates thrust, exhaust velocity, required fuel mass flow rate, specific fuel consumption, thermal efficiency, propulsive efficiency, and overall efficiency.
- Visualizees temperature and pressure throughout the engine cycle with graphs.
- Uses a GUI built on Tkinter for easy usage
- Dynamically created GUI allowing for easy addition of inputs or performance metrics

## Background and Methodology
This project was an independent, self-directed study of turbojet engines, applying the fields of thermodynamics and fluid dynamics in order to accurately calculate various performance metrics.

I began this project with zero thermodynamics or fluid dynamics knowledge. I used the foundation of my high-school physics, calculus, and chemistry classes to teach myself from the ground up the knowledge I would need in order to perform an accurate analysis of a turbojet engine, using the ideal Brayton cycle. 

My goal was to not simply be able to plug in inputs and output arbitrary numbers, but to actually understand the underlying thermodynamic concepts and processes behind a turbojet engine, as well as understand the derivation of common equations, such as for thrust.

I decided to consolidate my learning into a Python app as a way to practice my coding, as well as create an actual product that can be used to explore how various design choices impact the performance and efficiency of a turbojet engine.

## Demo
With all fields blank:
<img width="1919" height="867" alt="Screenshot 2025-09-09 131202" src="https://github.com/user-attachments/assets/a6a16e67-4f86-4d6c-98f5-2b91aeb2e60b" />


After inputting all parameters (example):
<img width="1918" height="855" alt="Screenshot 2025-09-09 131314" src="https://github.com/user-attachments/assets/d6b59eec-bb64-471d-ab54-4de93705ec7c" />

## Usage
Run the Python app:
  -> python src/main.py


