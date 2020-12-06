:: make
docker run -it --name blua nickblah/lua:5.1-alpine
:: /bin/bash

:: -e PGID=1000 -e PUID=1000 ^
:: --volume sandbox:/bin --hostname lua --rm 

