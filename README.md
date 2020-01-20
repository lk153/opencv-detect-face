## OPENCV 4

#### BUILD:
```
docker build -t viet/opencv .
```

#### RUN:
```
docker run -it --name opencv1 viet/opencv /bin/bash
```

#### REMOVE ALL:
```
docker stop opencv1
docker rm opencv1
docker rmi viet/opencv
docker rmi ubuntu:16.04
```