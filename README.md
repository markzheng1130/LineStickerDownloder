### Line Sticker Downloader as a Service
* For starting local test
In command line, run python3 flasky.py

* For starting docker container
    1. docker pull markzheng1130/line_sticker_downloader
    2. docker run -d -p 80:8888 --name line_sticker_downloader markzheng1130/line_sticker_downloader
    3. Open 127.0.0.1:80 in your web browser
    4. Try to download "https://store.line.me/stickershop/product/12378/zh-Hant"

* How to update docker image
    * re-build docker image
    ```
    docker build -t markzheng1130/line_sticker_downloader -f dockerfile . --no-cache
    docker push markzheng1130/line_sticker_downloader
    docker pull markzheng1130/line_sticker_downloader
    ```
  
    * run docker image in local
    ```
    docker rm {{ container_hash_id }}
    docker run -d -p 80:8888 --name line_sticker_downloader markzheng1130/line_sticker_downloader
    open 127.0.0.1:80
    ```
