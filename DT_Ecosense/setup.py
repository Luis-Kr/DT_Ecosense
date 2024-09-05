from setuptools import setup, Extension
import numpy

# Define the extension module
module = Extension(
    'extract_frames_module',  # Module name in Python
    include_dirs=[numpy.get_include(), '/usr/include/opencv4'],  # Paths to include directories
    libraries=['opencv_core', 'opencv_imgcodecs', 'opencv_videoio'],  # OpenCV libraries
    library_dirs=['/usr/local/lib'],  # Library directory for OpenCV
    sources=['src/extract_frames.cpp'],  # Path to the C++ source file
    extra_compile_args=['-std=c++11']  # Enable C++11 support
)

# Setup script to build the module
setup(
    name='extract_frames_module',  # Name of the package
    version='1.0',
    description='A CPython module to extract frames from a video',
    ext_modules=[module]  # Extension module to compile
)
