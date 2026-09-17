'''
dimension calculation
aspect ratio
scale
Pillow resizing
GIF frame processing
saving resized image
'''
from pathlib import Path
from PIL import Image
from src.domain.schemas.resize import ResizeRequest

class ResizeService:
    def __validate_request(self,request)->bool:
        
        new_w = request.width
        new_h = request.height
        scale = request.scale
        if new_w is not None and new_w < 0:
            raise ValueError("Width must be greater than 0")

        if new_h is not None and new_h < 0:
            raise ValueError("Height must be greater than 0")

        if scale is not None and scale <= 0:
            raise ValueError("Scale must be greater than 0")
        
    def __resize_method(self,ori_w:int, ori_h: int, request: ResizeRequest):
        """resizing dimension parameter"""
        
        new_width, new_height = 0,0
        new_w = request.width
        new_h = request.height
        scale = request.scale
        maintain_aspect_ratio = request.maintain_aspect_ratio 
        if not (
            (new_w is not None)
            ^ (new_h is not None)
            ^ (scale is not None)
        ):
            raise ValueError(
                "Exactly one of width, height, or scale must be provided"
            )
            
        if not maintain_aspect_ratio:
            print("[Resize-Service] Original image, not maintain aspect ratio not implemented yet")
            return ori_w,ori_h

        if new_w is not None and new_w >0 :
            new_width = new_w
            new_height = int((new_w/ori_w) * ori_h)
        elif new_h is not None and new_h > 0:
            new_height = new_h
            new_width = int((new_h/ori_h) * ori_w)
        elif scale is not None and scale > 0:
            new_height = int(scale * ori_h)
            new_width = int(scale * ori_w)
        print(
            f"[Resize-Service] Resized Image New Width : {new_width} | "
            f"New Height : {new_h}"
        )
        return new_width, new_height

    def calc_new_dimension(self,image: Image, request: ResizeRequest)->tuple[int,int]:
        """Calculate the target dimensions for resizing."""
        self.__validate_request(request)
        ori_w, ori_h = image.size
        
        new_w, new_h = self.__resize_method(
            ori_w=ori_w,
            ori_h=ori_h,
            request= request
        )
        return new_w,new_h
    
    def resize_image(self,image:Image,width: int,height: int):
        """Resize image to target dimension"""
        return image.resize(
            (width,height),
            Image.Resampling.LANCZOS
        )
        