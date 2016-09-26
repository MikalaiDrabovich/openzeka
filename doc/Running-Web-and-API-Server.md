# Running Web Server
You can run OpenZeka with GPU or CPU
## Start web server with GPU
    ./run-webserver-gpu.sh
## Start web server with CPU
    ./run-webserver-cpu.sh

Point your web browser to http://localhost:5000/

**It is important! First run will setup database.** Without this process API can not work.
# Running API Server
 Also OpenZeka API can run with GPU or CPU
## Start API with GPU
    ./run-apiserver-gpu.sh
## Start API with CPU
    ./run-apiserver-cpu.sh

API works *http://localhost:9000* you check API health with web browser.
### First web server run OpenZeka creates database with two account
 You can make use of the following users:
 - email `user@example.com` with password `Password1`.
 - email `admin@example.com` with password `Password1`.