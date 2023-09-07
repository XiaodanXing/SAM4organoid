import numpy as np
import cv2
import copy
import math
def remove_edge_cells(mask_image):
    w,h = mask_image.shape
    pruned_mask = copy.deepcopy(mask_image)
    remove_list = []
    edges = mask_image[0,:],mask_image[w-1,:],mask_image[:,0],mask_image[:,h-1]
    for edge in edges:
        edge_masks = np.unique(edge)
        for edge_mask in edge_masks:
            remove_list.append(edge_mask)
            pruned_mask[np.where(mask_image==edge_mask)] = 0

    return pruned_mask


def remove_small_cells(mask_image,area_threshold=10000):
    w,h = mask_image.shape
    pruned_mask = copy.deepcopy(mask_image)
    for mask_index in np.unique(mask_image):
        # if mask_index == mask_image[330,640]:
        #     a = 1
        area = np.sum(mask_image == mask_index)
        if area < area_threshold:
            pruned_mask[np.where(mask_image == mask_index)] = 0


    return pruned_mask

def split_cell_masks(mask_image):
    # Convert the mask image to grayscale
    gray_mask = cv2.cvtColor(np.array(mask_image*255,dtype=np.uint8), cv2.COLOR_BGR2GRAY)

    # Find unique RGB values in the mask image
    unique_colors = np.unique(mask_image.reshape(-1, mask_image.shape[2]), axis=0)

    # Create an empty index mask
    index_mask = np.zeros_like(gray_mask)

    # Assign unique index values to each cell in the index mask
    for i, color in enumerate(unique_colors):
        # Find pixels with the current color in the mask image
        color_mask = np.all(mask_image == color, axis=2)

        # Assign the index value to the corresponding pixels in the index mask
        index_mask[color_mask] = i + 1

    index_mask[np.where(gray_mask==255)]=0

    return index_mask


def remove_concentric_masks(mask_image):
    # Convert the mask image to grayscale
    cell_values = np.unique(mask_image)
    for i in range(1, len(cell_values)):# remove background
        mask_one = np.array(mask_image == cell_values[i],dtype=np.uint8)
        # mask_one_dilated = cv2.dilate(mask_one, np.ones((5, 5), np.uint8),100)
        # xmin, xmax, ymin, ymax = np.min(np.where(mask_one == 1)[0]), np.max(np.where(mask_one == 1)[0]),\
        #     np.min(np.where(mask_one == 1)[1]), np.max(np.where(mask_one == 1)[1]),
        contour, _ = cv2.findContours(mask_one, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contour) > 0:
            largest_contour = max(contour, key=cv2.contourArea)

            mask_image = cv2.drawContours(mask_image, [largest_contour], -1, (np.int(cell_values[i])), thickness=cv2.FILLED)



    return mask_image



def analyze_cell_properties(mask):
    properties = {}

    # Calculate properties from the mask
    contour, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_idx = np.argmax([len(contour[i]) for i in range(len(contour))])


    perimeter = cv2.arcLength(contour[contour_idx], True)

    area = cv2.contourArea(contour[contour_idx])

    _, radius = cv2.minEnclosingCircle(contour[contour_idx])

    ellipse = cv2.fitEllipse(contour[contour_idx])
    ellipse_contour = cv2.ellipse2Poly((int(ellipse[0][0]), int(ellipse[0][1])),
                                       (int(ellipse[1][0] * 0.5), int(ellipse[1][1] * 0.5)),
                                       int(ellipse[2]), 0, 360, 5)

    # Compute the perimeter of the fitted ellipse
    perimeter_ellipse = cv2.arcLength(ellipse_contour, closed=True)

    # Compute the smoothness as the ratio of perimeters
    smoothness = perimeter_ellipse / perimeter

    compactness = abs((perimeter ** 2) / (area * 4 * math.pi) - 1)

    symmetry = cv2.matchShapes(contour[contour_idx], cv2.convexHull(contour[contour_idx], returnPoints=True), 1, 0.0)

    # Store the properties
    properties['perimeter'] = perimeter
    properties['area'] = area
    properties['radius'] = radius
    properties['non-smoothness'] = smoothness
    properties['non-circularity'] = compactness
    # properties['concavity'] = concavity
    properties['symmetry'] = symmetry

    return properties


