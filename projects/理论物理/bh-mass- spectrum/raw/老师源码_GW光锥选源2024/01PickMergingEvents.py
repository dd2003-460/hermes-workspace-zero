# -*- coding: utf-8 -*-
"""
Created on Sun May 12 15:51:14 2024

@author: Qing
"""

import os
import pandas as pd
import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt
from scipy import interpolate
#定义参数
c=2.9979e8
H=72
a_dot=H
G=6.67e-11
pi=3.14159265359
k=-1#R-W度规
rhox0=6.66e-2;#宇宙学常数
rhom0=2.33e-4
rhoR0=1.23e-3#radiation
rhocr=3*H**2/(8*pi*G) #matter
Omegam=rhom0/rhocr
Omegam=0.3
Omegax=rhox0/rhocr
Omegax=0.7
Omegak=-k/H**2
Omegak=0
OmegaR=1-Omegam-Omegax-Omegak
OmegaR=0
# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构建文件的绝对路径
file_path = os.path.join(script_dir, 'result.csv')
# Define the number of rows to skip for the header section
header_rows = 19

# Read the CSV file into a pandas DataFrame, skipping the header section
df = pd.read_csv(file_path,skiprows=header_rows,skipfooter=1)

# Define the function to calculate the co-moving distance
def coMovingDistance(z):
    a_z = 1 / (1 + z)
    F = lambda a: c / (a * a * a_dot * np.sqrt(Omegax + Omegam / a**3 + OmegaR / a**4 + Omegak / a**2))
    X, _ = spi.quad(F, a_z, 1)
    return X

# Create an empty list to store the merging cases
merging_cases = []


#####################


# Store merged galaxies
#df['coMovingDistance'] = -1
#for index, row in df.iterrows():
#    first_progenitor_id = row['firstProgenitorId']
#    if first_progenitor_id != -1:
#        first_progenitor_row = df[df['galaxyid'] == first_progenitor_id]
#        if first_progenitor_row['nextProgenitorId'].values[0] != -1:
#            merged_galaxy_distance = coMovingDistance(row['redshift'])
#            df.at[index, 'coMovingDistance'] = merged_galaxy_distance
#            
#            # Record the merging case data
#            merging_case = {
#                'galaxyid_merged': row['galaxyid'],
#                'haloid_merged': row['haloid'],
#                'galaxyid_1': first_progenitor_id,
#                'galaxyid_2': first_progenitor_row['nextProgenitorId'].values[0],
#                'redshift': row['redshift'],
#                'snapnum': row['snapnum'],
#                'x': row['x'],
#                'y': row['y'],
#                'z': row['z'],
#                'stellarMass': row['stellarMass'],
#                'bulgeMass': row['bulgeMass'],
#                'blackHoleMass': row['blackHoleMass']
#            }
#            merging_cases.append(merging_case)

for index, row in df.iterrows():
    first_progenitor_id = row['firstProgenitorId']
    if first_progenitor_id != -1:
        first_progenitor_row = df[df['galaxyid'] == first_progenitor_id]
        if first_progenitor_row['nextProgenitorId'].values[0] != -1:
            # Getting blackHoleMass for first_progenitor_id
            first_progenitor_black_hole_mass = first_progenitor_row['blackHoleMass'].values[0]
            
            # Getting blackHoleMass for nextProgenitorId
            next_progenitor_id = first_progenitor_row['nextProgenitorId'].values[0]
            next_progenitor_row = df[df['galaxyid'] == next_progenitor_id]
            next_progenitor_black_hole_mass = next_progenitor_row['blackHoleMass'].values[0]
            
            # Check if both black hole masses are not zero
            if first_progenitor_black_hole_mass != 0 and next_progenitor_black_hole_mass != 0:
                # Calculate merged galaxy distance
                merged_galaxy_distance = coMovingDistance(row['redshift'])
                df.at[index, 'coMovingDistance'] = merged_galaxy_distance
                
                # Record the merging case data with additional blackHoleMass information
                merging_case = {
                    'galaxyid_merged': row['galaxyid'],
                    'haloid_merged': row['haloid'],
                    'galaxyid_1': first_progenitor_id,
                    'galaxyid_2': first_progenitor_row['nextProgenitorId'].values[0],
                    'redshift': row['redshift'],
                    'snapnum': row['snapnum'],
                    'x': row['x'],
                    'y': row['y'],
                    'z': row['z'],
                    'stellarMass': row['stellarMass'],
                    'bulgeMass': row['bulgeMass'],
                    'blackHoleMass': row['blackHoleMass'],
                    'first_progenitor_blackHoleMass': first_progenitor_black_hole_mass,
                    'next_progenitor_blackHoleMass': next_progenitor_black_hole_mass
                }
                merging_cases.append(merging_case)




# Create a new DataFrame to store the merging cases
merging_cases_df = pd.DataFrame(merging_cases)

# Save the merging cases DataFrame to a new CSV file
merging_cases_df.to_csv('merging_cases.csv', index=False)


#####################





print('1')