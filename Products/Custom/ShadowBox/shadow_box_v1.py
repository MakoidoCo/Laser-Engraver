import torch
import numpy as np
import cv2
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

model_types = ("DPT_Large", "DPT_Hybrid", "MiDaS_small")
# cv2.COLORMAP_MAGMA
class DepthEstimator:
    def __init__(self, model_type="MiDaS_small", colormap=None):
        self.model_type = model_type
        self.colormap = colormap
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.midas = torch.hub.load("intel-isl/MiDaS", self.model_type)
        self.midas.to(self.device)
        self.midas.eval()
        midas_transform = torch.hub.load("intel-isl/MiDaS", "transforms")
        if self.model_type in ["DPT_Large", "DPT_Hybrid"]:
            self.transform = midas_transform.dpt_transform
        else:
            self.transform = midas_transform.small_transform

    def estimate_depth(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("The image path is invalid or the image cannot be loaded.")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = self.transform(img_rgb).to(self.device)

        with torch.no_grad():
            prediction = self.midas(img_tensor)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bicubic",
                align_corners=False
            ).squeeze()

        depth_map = prediction.cpu().numpy()
        depth_map = cv2.normalize(depth_map, None, 0, 1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_64F)
        depth_map = (depth_map * 255).astype(np.uint8)
        if self.colormap: depth_map = cv2.applyColorMap(depth_map, self.colormap)
        output_path = self.get_output_path(image_path)
        cv2.imwrite(output_path, depth_map)

    def get_output_path(self, image_path):
        folder_path = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(folder_path, f"{base_name}_depth.png")
        return output_path

def main():
    root = Tk()
    root.withdraw()
    image_path = askopenfilename(title="Select image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    
    if not image_path:
        return
    estimator = DepthEstimator(model_type=model_types[0])
    estimator.estimate_depth(image_path)

if __name__ == "__main__":
    main()
