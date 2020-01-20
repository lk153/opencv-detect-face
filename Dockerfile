FROM ubuntu:16.04

RUN cd / && mkdir viet-test && cd viet-test && \
    rm -rf opencv/build && \
    rm -rf opencv_contrib/build && \
    mkdir installation && \
    mkdir installation/OpenCV-master && \
    apt-get update && \
    apt-get install sudo -y

RUN sudo apt -y update && \
    sudo apt -y upgrade && \
    sudo apt -y remove x264 libx264-dev && \
    sudo apt -y install build-essential checkinstall cmake pkg-config yasm && \
    sudo apt -y install git gfortran && \
    sudo apt -y install libjpeg8-dev libjasper-dev libpng12-dev && \
    sudo apt -y install libtiff5-dev && \
    sudo apt -y install libtiff-dev && \
    sudo apt -y install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev && \
    sudo apt -y install libxine2-dev libv4l-dev

RUN cd /usr/include/linux

RUN sudo ln -s -f ../libv4l1-videodev.h videodev.h

WORKDIR /viet-test

RUN sudo apt -y install libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev && \
    sudo apt -y install libgtk2.0-dev libtbb-dev qt5-default && \
    sudo apt -y install libatlas-base-dev && \
    sudo apt -y install libfaac-dev libmp3lame-dev libtheora-dev && \
    sudo apt -y install libvorbis-dev libxvidcore-dev && \
    sudo apt -y install libopencore-amrnb-dev libopencore-amrwb-dev && \
    sudo apt -y install libavresample-dev && \
    sudo apt -y install x264 v4l-utils && \
    sudo apt -y install libprotobuf-dev protobuf-compiler && \
    sudo apt -y install libgoogle-glog-dev libgflags-dev && \
    sudo apt -y install libgphoto2-dev libeigen3-dev libhdf5-dev doxygen

RUN sudo apt -y install python3-dev python3-pip && \
    sudo -H pip3 install -U pip numpy && \
    sudo apt -y install python3-testresources && \
    sudo apt-get -y install python3-venv

RUN python3 -m venv OpenCV-master-py3 && \
    echo "# Virtual Environment Wrapper" >> ~/.bashrc && \
    echo "alias workoncv-master=\"source /viet-test/OpenCV-master-py3/bin/activate\"" >> ~/.bashrc

RUN . OpenCV-master-py3/bin/activate && \
    pip install --upgrade pip && \
    pip install wheel numpy scipy matplotlib scikit-image scikit-learn ipython dlib mysql-connector-python env-file && \
    deactivate

RUN git clone https://github.com/opencv/opencv.git && \
    cd opencv && \
    git checkout master && \
    cd .. && \
    git clone https://github.com/opencv/opencv_contrib.git && \
    cd opencv_contrib && \
    git checkout master && \
    cd ..

RUN cd opencv && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
            -D CMAKE_INSTALL_PREFIX=/viet-test/installation/OpenCV-master \
            -D INSTALL_C_EXAMPLES=ON \
            -D INSTALL_PYTHON_EXAMPLES=ON \
            -D WITH_TBB=ON \
            -D WITH_V4L=ON \
            -D OPENCV_PYTHON3_INSTALL_PATH=/viet-test/OpenCV-master-py3/lib/python3.5/site-packages \
        -D WITH_QT=ON \
        -D WITH_OPENGL=ON \
        -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
        -D BUILD_EXAMPLES=ON ..

WORKDIR /viet-test/opencv/build
RUN make -j2 && \
    make install

COPY . /viet-test
WORKDIR /viet-test