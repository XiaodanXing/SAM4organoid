import copy
import os
from utils import analyze_cell_properties,split_cell_masks,remove_edge_cells,remove_small_cells,remove_concentric_masks
import numpy as np
import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import cv2

## get model
sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

device = "cuda:0"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
mask_generator = SamAutomaticMaskGenerator(sam)



def combine_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    # ax = plt.gca()
    # ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        xmin,ymin,xmax,ymax = ann['bbox']

        if abs(xmin-0) <5 and abs(ymin-0) <5 and abs(xmax-sorted_anns[0]['segmentation'].shape[0]) <5 \
                and abs(ymax-sorted_anns[0]['segmentation'].shape[1]) <5:
            pass
        else:
            color_mask = np.concatenate([np.random.random(3), [0.35]])
            img[m] = color_mask
    # ax.imshow(img)
    return img



def patch_property(image,start_idx):


    masks = mask_generator.generate(image)

    # combine the annotations generated from SAM
    final_mask = combine_anns(masks)

    # indexing the objects in the segmentation mask
    index_mask = split_cell_masks(final_mask)


    pruned_mask = remove_edge_cells(index_mask)
    pruned_mask_reduce = remove_small_cells(pruned_mask,area_threshold=1500)
    pruned_mask_reduce = remove_concentric_masks(pruned_mask_reduce)
    cell_mask = np.zeros((pruned_mask.shape[0],pruned_mask.shape[1],3))

    cell_num = len(np.unique(pruned_mask_reduce)) - 1
    properties = {}
    for i in range(1, cell_num+1):# remove background
        mask_one = np.array(pruned_mask_reduce == np.unique(pruned_mask_reduce)[i],dtype=np.uint8)
        try:
            properties['cell %i'%(i+start_idx)] = analyze_cell_properties(mask_one)
            cell_color = (np.random.randint(255),
                                                       np.random.randint(255),
                                                       np.random.randint(255))
            # cell_mask[np.where(mask_one==1)[0],np.where(mask_one==1)[1],:] = (255,0,0)
            contours, hierarchy = cv2.findContours(mask_one, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(cell_mask, contours, -1, cell_color, 3)

            text = str(i+start_idx)
            # Define the font properties
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            font_color = cell_color  # White color (BGR format)
            thickness = 3

            # Find the size of the text
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)

            # Calculate the position to center the text on the image
            text_x = ( np.max(np.where(mask_one==1)[0]) - np.min(np.where(mask_one==1)[0]))//2 + np.min(np.where(mask_one==1)[0])
            text_y = ( np.max(np.where(mask_one==1)[1]) - np.min(np.where(mask_one==1)[1]))//2 + np.min(np.where(mask_one==1)[1])

            # Add the text to the image
            cell_mask = cv2.putText(cell_mask, text, (text_y, text_x), font, font_scale, font_color, thickness)
        except ZeroDivisionError:
            pass
    cell_mask = cv2.addWeighted(np.array(cell_mask, dtype=np.uint8), 1, image, 1, 0)
    return properties, cell_num + start_idx, cell_mask

