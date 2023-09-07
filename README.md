# SAM4organoid

This repository is associated with our paper "SegmentAnything helps microscopy images based automatic and quantitative organoid detection and analysis," which focuses on automatic and quantitative organoid detection and analysis in microscopy images.

Organoids are self-organized 3D cell clusters that closely mimic the architecture and function of in vivo tissues and organs. Quantification of organoid morphology helps in studying organ development, drug discovery, and toxicity assessment. Recent microscopy techniques provide a potent tool to acquire organoid morphology features, but manual image analysis remains a labor and time-intensive process. Thus, this paper proposes a comprehensive pipeline for microscopy analysis that leverages the SegmentAnything to precisely demarcate individual organoids. Additionally, we introduce a set of morphological properties, including perimeter, area, radius, non-smoothness, and non-circularity, allowing researchers to analyze the organoid structures quantitatively and automatically. 

In our paper, we conducted tests on bright-field images of human induced pluripotent stem cells (iPSCs) derived neural-epithelial (NE) organoids. The results obtained from our automatic pipeline closely align with manual organoid detection and measurement, showcasing the capability of our proposed method in accelerating organoid morphology analysis.

![flowchart](https://github.com/XiaodanXing/SAM4organoid/assets/30890745/03b8a3b2-96d4-4797-80d9-3bcf361fe8b6)


## Method description

In our research, we leveraged the Python API for SegmentAnything and evaluated three pre-trained models. However, we encountered several challenges when working with SegmentAnything-generated masks, as illustrated in Figure below, which necessitated post-processing for accurate cell identification.

![challenge](https://github.com/XiaodanXing/SAM4organoid/assets/30890745/16c1eeef-d174-4a1f-b8a2-79b48db282d5)


The challenges we faced included:

1. SegmentAnything occasionally misidentified the background as an object, resulting in non-zero indices for the background in the masks.

2. High-resolution microscopy images required the use of cropped patches for model fitting, introducing incomplete organoids along the patch edges, leading to erroneous morphological analysis. To address this, we implemented an automated process to exclude objects near patch boundaries.

3. Some organoids with a lumen structure were inaccurately demarcated into two separate objects. We resolved this issue by computing the maximum boundary of each mask and unifying values within this boundary.

4. Debris could be erroneously identified as organoids by the model. Although we haven't yet found an automated method to remove them, we manually marked and deleted these non-organoid structures, which proved to be a relatively simpler task compared to manual organoid identification.

**Property Analysis**:

We conducted a comprehensive analysis of each organoid, computing five distinct properties to characterize their characteristics:

1. **Perimeter**: Quantifies the total length of the organoid's boundary, providing a measure of its overall shape complexity.

2. **Radius**: Estimates the organoid's size by calculating the average distance from the center of the cell to various points on its perimeter.

3. **Area**: Corresponds to the number of pixels encompassed within the organoid, serving as a direct indicator of its size.

4. **Non-smoothness**: Reflects the local variation in radius lengths along the organoid boundary. A higher non-smoothness value indicates a more irregular and less smooth boundary. To compute this property, we fitted an ellipse to the organoid’s boundary and determined the smoothness as the ratio of perimeters between the fitted ellipse and the original contour.

5. **Non-circularity**: We employed the following equation to evaluate the extent to which the organoid resembles a perfect circle: $$
\text{Non-circularity} = \left| \frac{{\text{Perimeter}^2}}{{4\pi \times \text{Area}}} - 1 \right|
$$

