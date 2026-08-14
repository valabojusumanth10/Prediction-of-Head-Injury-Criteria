import pandas as pd
import numpy as np

np.random.seed(42)
n = 500

hood_length = np.random.uniform(900, 1600, n)
hood_width = np.random.uniform(1200, 1800, n)
hood_thickness = np.random.uniform(0.6, 1.5, n)
material_density = np.random.uniform(2100, 7900, n)
youngs_modulus = np.random.uniform(45, 210, n)
poisson_ratio = np.random.uniform(0.25, 0.40, n)
yield_strength = np.random.uniform(150, 550, n)
impact_velocity = np.random.uniform(6.5, 11.1, n)
impact_angle = np.random.uniform(50, 80, n)
hood_mass = np.random.uniform(8, 20, n)
stiffness = np.random.uniform(20000, 100000, n)
energy_absorption = np.random.uniform(400, 1500, n)

hic_value = (
    0.8 * impact_velocity**2 * 100
    + 0.3 * impact_angle
    - 0.2 * energy_absorption
    + 0.001 * stiffness * 0.01
    + 0.5 * material_density * 0.01
    - 0.4 * hood_thickness * 100
    + np.random.normal(0, 80, n)
)
hic_value = np.clip(hic_value, 200, 3000)

df = pd.DataFrame({
    'hood_length': np.round(hood_length, 2),
    'hood_width': np.round(hood_width, 2),
    'hood_thickness': np.round(hood_thickness, 3),
    'material_density': np.round(material_density, 2),
    'youngs_modulus': np.round(youngs_modulus, 2),
    'poisson_ratio': np.round(poisson_ratio, 3),
    'yield_strength': np.round(yield_strength, 2),
    'impact_velocity': np.round(impact_velocity, 2),
    'impact_angle': np.round(impact_angle, 2),
    'hood_mass': np.round(hood_mass, 2),
    'stiffness': np.round(stiffness, 2),
    'energy_absorption': np.round(energy_absorption, 2),
    'hic_value': np.round(hic_value, 2),
})

df.to_csv('vehicle_hood_dataset.csv', index=False)
print(f"Dataset generated: {len(df)} rows")
print(df.head())
print(f"\nHIC range: {df['hic_value'].min():.2f} to {df['hic_value'].max():.2f}")