'''
dimension calculation
aspect ratio
scale
Pillow resizing
GIF frame processing
saving resized image
'''

from PIL import Image, ImageSequence
from src.domain.schemas.resize import ResizeRequest, ResizedGIF
    
class ResizeService:
    def __validate_request(self,request)->bool:
        default_value = 0
        new_w = request.width
        new_h = request.height
        scale = request.scale
        if new_w is not None and new_w < default_value:
            raise ValueError("Width must be greater than 0")

        if new_h is not None and new_h < default_value:
            raise ValueError("Height must be greater than 0")

        if scale is not None and scale < default_value:
            raise ValueError("Scale must be greater than 0")
        
    def __resize_method(self,ori_w:int, ori_h: int, request: ResizeRequest):
        """resizing dimension parameter"""
        new_width, new_height = 0,0
        new_w = request.width
        new_h = request.height
        scale = request.scale
        print(f"new_w : {new_w}, new_h : {new_h}, scale : {scale}")
        maintain_aspect_ratio = request.maintain_aspect_ratio 
        # if not (
        #     (new_w is not None)
        #     ^ (new_h is not None)
        #     ^ (scale is not None)
        # ):
        #     raise ValueError(
        #         "Exactly one of width, height, or scale must be provided"
        #     )
        
        if not maintain_aspect_ratio:
            if new_w is not None and new_h is not None and scale is None:
                new_width = new_w
                new_height = new_h
        else:
            if new_w is not None :
                new_width = new_w
                new_height = int((new_w/ori_w) * ori_h)
            elif new_h is not None:
                new_height = new_h
                new_width = int((new_h/ori_h) * ori_w)
            elif scale is not None:
                new_height = int(scale * ori_h)
                new_width = int(scale * ori_w)
        print(
            f"[Resize-Service] Resized Image New Width : {new_width} | "
            f"New Height : {new_height}"
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
    
    def resize_image(self,image:Image, width: int,height: int)->Image.Image | list[Image.Image]:
        """Resize image to target dimension"""
            
        resized_image = image.resize(
            (width,height),
            Image.Resampling.LANCZOS
        )
        
        return resized_image
    #disposal is a setting that tells the GIF player what to do with the previous frame before drawing the next frame
    def resize_gif(self,image:Image,width:int,height:int)-> ResizedGIF:
        """Resize image for gif"""
        loop = image.info.get("loop",0)
        resized_frames = []
        durations = []
        
        for frame in ImageSequence.Iterator(image):
            resized_frame = frame.resize(
                (width,height),
                Image.NEAREST
            )
            
            duration = frame.info.get("duration",100)
            durations.append(duration)
           
            resized_frames.append(resized_frame)
        return ResizedGIF(
                            resized_frames = resized_frames,
                            durations=durations,
                            disposals=2, #disposals 2 mean we completely dispose the previous frame before saving the next frame
                            loop=loop
                    )
