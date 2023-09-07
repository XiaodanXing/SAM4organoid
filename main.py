import time
from analysis import patch_property
import os
from tifffile import imread
import argparse
import matplotlib
matplotlib.use('TkAgg')
import cv2
import pandas as pd


parser = argparse.ArgumentParser(description='Process microscopy images and save results')
parser.add_argument('-i','--input', type=str, help='Path to the directory containing PNG images')
parser.add_argument('-o','--output', type=str, help='Path to the directory containing segmentation masks and cell properties')
args = parser.parse_ars()


fpath = args.input
output_path = args.output

for file in os.listdir(fpath):
    if '.png' in file:
        fn = os.path.join(fpath,file)
        cell_properties = {}
        sta_time = time.time()
        cell_properties = {}
        try:
            image = cv2.imread(fn)
        except:
            image = imread(fn)

        # image preprocessing
        w, h, _ = image.shape
        w, h = int((w - 10000) / 2), int((h - 10000) / 2)

        # calculate properties
        cell_properties_patch,sta_idx, cell_mask_batch = patch_property(image,0)
        cell_properties.update(cell_properties_patch)

        # save segmentation mask and cell properties
        cv2.imwrite(os.path.join(output_path,file.strip('.png') +  '_cell_mask.png'),
        cell_mask_batch)

        cell_properties = pd.DataFrame.from_dict(cell_properties,orient='index')
        cell_properties.to_csv(os.path.join(output_path,
                                           file.replace('.png','.csv')))

        end_time = time.time()
        print('File %s completed, time used %0.2f min'%(fn,(end_time-sta_time)/60))