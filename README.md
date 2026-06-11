Asteroid Dashboard — NASA Small-Body Database

An interactive dashboard for exploring and analyzing Near-Earth Asteroids (NEAs), built with Python, Streamlit, and Plotly. The dataset comes from the NASA JPL Small-Body Database and contains 41,281 cataloged objects up to 2025.

About the Project

This project was developed as part of a college assignment with the goal of applying data analysis, visualization, and web development techniques to a real-world scientific dataset.

The dashboard transforms a complex astronomical database into an accessible and interactive interface, allowing users to explore orbital and physical characteristics of asteroids through dynamic visualizations and filtering tools. The application focuses on usability, performance, and clean code practices, including data caching, automatic dataset detection, and a custom space-themed interface.

Features
Automatic CSV file detection within the project directory and subfolders
Data cleaning and normalization pipeline
Interactive filtering by:
Orbital class
Potentially Hazardous Asteroid (PHA) status
Diameter range
Absolute magnitude (H)
Real-time dashboard updates based on user-selected filters
Support for manual CSV upload directly through the interface
Automatically generated insights based on filtered data
Dashboard Visualizations
Key Performance Indicators (KPIs)

Displays:

Total number of asteroids
Percentage of PHAs
Percentage with MOID below 0.05 AU
Percentage with orbital periods under 2 years
Percentage of asteroids larger than 1 km
Percentage Summary

Horizontal bar chart showing the proportion of asteroids that meet specific criteria, such as:

Named objects
PHAs
Near-Earth objects
Fast-orbit objects
High-luminosity objects
High-eccentricity objects
High-albedo objects
Estimated diameter availability
Large asteroids
Orbital Class Distribution

Donut chart displaying the ten most common orbital classes and their relative percentages.

Size Distribution

Categorizes asteroids into:

Small (< 100 m)
Medium (100 m – 1 km)
Large (> 1 km)
MOID vs Diameter

Scatter plot showing:

X-axis: Minimum Orbit Intersection Distance (MOID)
Y-axis: Diameter (logarithmic scale)

Points are colored according to PHA status, and a reference line highlights the 0.05 AU monitoring threshold.

Absolute Magnitude (H) vs Diameter

Visualizes the relationship between an asteroid's intrinsic brightness and its estimated size, with points colored by orbital class.

Orbital Eccentricity by Class

Boxplot comparing eccentricity distributions across the eight most frequent orbital classes.

Automatic Insights

The dashboard generates contextual observations based on the filtered dataset, including:

Alerts when the percentage of PHAs exceeds 5%
Percentage of objects within the near-Earth monitoring zone
Dominant orbital class
Presence of large asteroids
Median absolute magnitude (H)
Technologies Used
Python 3
Streamlit
Plotly
Pandas
Custom CSS
Google Fonts (Orbitron and Exo 2)
Installation

Install the required dependencies:

pip install streamlit plotly pandas

Place the asteroid CSV file in the project directory. Files containing keywords such as:

asteroid
asteroide
nea
pha

will be automatically detected.

Run the application:

streamlit run nasanovoc_comentado.py
Data Source

NASA JPL Small-Body Database

Official catalog of small bodies in the Solar System maintained by NASA's Jet Propulsion Laboratory (JPL).

Academic Purpose

This project was developed for academic purposes to practice data analysis, data visualization, and dashboard development using real NASA data. It demonstrates the application of Python-based tools for transforming raw scientific datasets into interactive and meaningful insights.
