from vimba import *
import sys
from typing import Optional
import cv2

class MakoCamera():
    
    def abort(self, reason: str, return_code: int = 1, usage: bool = False):
        print(reason + '\n')
   
        sys.exit(return_code)
        
    def setup_camera(cam: Camera):
        with cam:
            # Enable auto exposure time setting if camera supports it
            try:
                cam.ExposureAuto.set('Continuous')

            except (AttributeError, VimbaFeatureError):
                pass

            # Enable white balancing if camera supports it
            try:
                cam.BalanceWhiteAuto.set('Continuous')

            except (AttributeError, VimbaFeatureError):
                pass

            # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
            try:
                cam.GVSPAdjustPacketSize.run()

                while not cam.GVSPAdjustPacketSize.is_done():
                    pass

            except (AttributeError, VimbaFeatureError):
                pass
            # Query available, open_cv compatible pixel formats
            # prefer color formats over monochrome formats
            cv_fmts = intersect_pixel_formats(cam.get_pixel_formats(), OPENCV_PIXEL_FORMATS)
            color_fmts = intersect_pixel_formats(cv_fmts, COLOR_PIXEL_FORMATS)

            if color_fmts:
                cam.set_pixel_format(color_fmts[0])

            else:
                mono_fmts = intersect_pixel_formats(cv_fmts, MONO_PIXEL_FORMATS)

                if mono_fmts:
                    cam.set_pixel_format(mono_fmts[0])

                else:
                    abort('Camera does not support a OpenCV compatible format natively. Abort.')
    def parse_args(self) -> Optional[str]:
        
        args = sys.argv[1:]
        argc = len(args)

        for arg in args:
            if arg in ('/h', '-h'):
                self.print_usage()
                sys.exit(0)

        if argc > 1:
            self.abort(reason="Invalid number of arguments. Abort.", return_code=2, usage=True)

        return None if argc == 0 else args[0]

    def get_camera(self, camera_id: Optional[str]) -> Camera:
        with Vimba.get_instance() as vimba:
            if camera_id:
                try:
                    return vimba.get_camera_by_id(camera_id)

                except VimbaCameraError:
                    self.abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

            else:
                cams = vimba.get_all_cameras()
                if not cams:
                    self.abort('No Cameras accessible. Abort.')

                return cams[0]

if __name__ == '__main__':
    cam = MakoCameraExtOpenCVFrame()
    cam_id = cam.parse_args()
    with Vimba.get_instance() as vimba:
        with cam.get_camera(cam_id) as cam:
            cam.setup_camera(cam)
            cams = vimba.get_all_cameras ()
            with cams [0] as cam:
                frame = cam.get_frame ()
                frame. convert_pixel_format ( PixelFormat.Mono8)
                cv2. imwrite ('frame.jpg ', frame. as_opencv_image ())
    

         