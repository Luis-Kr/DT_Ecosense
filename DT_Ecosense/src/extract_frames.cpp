#include <Python.h>
#include <opencv2/opencv.hpp>

static PyObject* extract_frames(PyObject* self, PyObject* args) {
    PyObject* logger;
    const char* video_path;
    const char* output_dir;
    int frame_number;

    if (!PyArg_ParseTuple(args, "Ossi|i", &logger, &video_path, &output_dir, &frame_number)) {
        return NULL;
    }

    cv::VideoCapture video_capture(video_path);
    if (!video_capture.isOpened()) {
        PyObject_CallMethod(logger, "info", "s", "Error: Could not open video.");
        Py_RETURN_NONE;
    }

    double fps = video_capture.get(cv::CAP_PROP_FPS);
    if (fps == 0) {
        PyObject_CallMethod(logger, "info", "s", "Error: Could not retrieve frame rate.");
        Py_RETURN_NONE;
    }

    PyObject_CallMethod(logger, "info", "s", ("Frame rate: " + std::to_string(fps)).c_str());
    PyObject_CallMethod(logger, "info", "s", ("Extracting frames from video '" + std::string(video_path) + "'...").c_str());

    // Calculate the frame number corresponding to each 10s interval
    int frames_per_minute = static_cast<int>(fps * 10);

    while (true) {
        // Set the video capture position to the next frame of interest
        video_capture.set(cv::CAP_PROP_POS_FRAMES, frame_number);

        cv::Mat frame;
        bool ret = video_capture.read(frame);
        if (!ret) {
            break;
        }

        // Save one frame per interval
        if (frame_number % frames_per_minute == 0) {
            std::string frame_filename = std::string(output_dir) + "/frame_" + std::to_string(frame_number / frames_per_minute) + ".jpg";
            cv::imwrite(frame_filename, frame);
        }

        // Increment frame_number by frames_per_minute to skip frames
        frame_number += frames_per_minute;
    }

    video_capture.release();
    PyObject_CallMethod(logger, "info", "s", "All frames extracted.");
    PyObject_CallMethod(logger, "info", "s", ("frame_number: " + std::to_string(frame_number)).c_str());

    return Py_BuildValue("i", frame_number);
}

// Method definition object for this extension
static PyMethodDef ExtractFramesMethods[] = {
    {"extract_frames", extract_frames, METH_VARARGS, "Extract frames from a video."},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef extractframesmodule = {
    PyModuleDef_HEAD_INIT,
    "extract_frames_module",  // Module name
    NULL,                     // Module documentation
    -1,                       // Module state size (-1 means global)
    ExtractFramesMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_extract_frames_module(void) {
    return PyModule_Create(&extractframesmodule);
}


// while (true) {
//         frame_number++;
//         cv::Mat frame;
//         bool ret = video_capture.read(frame);
//         if (!ret) {
//             break;
//         }

//         // Calculate the frame number corresponding to each minute
//         int frames_per_minute = static_cast<int>(fps * 60);

//         // Save one frame per minute
//         if (frame_number % frames_per_minute == 0) {
//             std::string frame_filename = std::string(output_dir) + "/frame_" + std::to_string(frame_number / frames_per_minute) + ".jpg";
//             cv::imwrite(frame_filename, frame);
//         }
//     }