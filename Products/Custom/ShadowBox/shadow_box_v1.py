import cv2
# import tensorflow as tf
from tkinter.filedialog import askopenfilenames


class ImageManager:
    def __init__(self, resize: tuple = None, *, 
                 image_extensions: tuple = ("Image File","*.jpg *.jpeg *.png *.gif *.bmp *.tiff")) -> None:
        
        self.paths = askopenfilenames(title="Select one or more images", filetypes=[image_extensions])
        
        self.images = list()
        self.images_sizes = list()

        if isinstance(resize, tuple) or not resize: self.resize = resize
        else: raise TypeError("Must be a tuple")
            
    def run(self):
        self.__read_images()
        
    def __read_images(self):
        for path in self.paths: 
            timg = cv2.imread(path)
            if self.resize: timg = cv2.resize(timg, self.resize)
            tshape = timg.shape
            print((timg, tshape))
            self.images.append((timg, tshape))
        del timg
        del tshape


img_manager = ImageManager()
img_manager.run()

