from PIL import Image, ImageSequence
from src.domain.schemas.crop import CropRequest, CroppedGIF
from src.routes.image import ImageService

class CropService:
    def __validate_request(self,request: CropRequest):
        top_left = request.top_left_point
        bottom_right = request.bottom_right_point
        points = [top_left,bottom_right]
        top_left_x = top_left[0]
        bottom_right_x = bottom_right[0]
        
        if not all(coordinate>=0 for point in points for coordinate in point):
            raise ValueError("Cropping points must be greater or equal than 0")
        
        if top_left_x < bottom_right_x:
            raise ValueError("Top-left x must be left of bottom-right point")
        

    def crop(self,image:Image,request:CropRequest)->Image:
        self.__validate_request(request=request)
        points = [
                    request.top_left_point[0], 
                    request.top_left_point[1],
                    request.bottom_right_point[0],
                    request.bottom_right_point[1]
                ]
        new_image = image.crop(points)
        return new_image
        
    def crop_gif(self, image:Image, request:CropRequest)->CroppedGIF:
        """Crop image for gif"""
        loop = image.info.get("loop",0)
        resized_frames = []
        durations = []
        
        for frame in ImageSequence.Iterator(image):
            resized_frame = self.crop(image=frame, request=request)
            duration = frame.info.get("duration",100)
            durations.append(duration)
            resized_frames.append(resized_frame)
            
        return CroppedGIF(
                cropped_frames = resized_frames,
                durations = durations,
                disposals=2,
                loop = loop
        )