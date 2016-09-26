# API Usage
First run API Server
# Running API Server
 OpenZeka API can run with GPU or CPU
##Start API with GPU
    ./run-apiserver-gpu.sh
##Start API with CPU
    ./run-apiserver-cpu.sh
API runs 9000 port. You can visit http://localhost:9000 and check API health.

**Token Request:**
In order to create `client_id` and `client_secret` you need to access web server and *create an application.*

    curl -X POST "http://localhost:9000/oauth/token" \
        -d "client_id={client_id}" \
        -d "client_secret={client_secret}" \
        -d "grant_type=client_credentials"

**API Response:**

    {
      "access_token": "ePcfeKIZAQRdAMyWEONpjbYJjE3s3k",
      "token_type": "Bearer",
      "expires_in": 259200,
      "scope": "api_access"
    }

**Image Recognition Request (Local file):**
You need to change **imagefile=@to you local image file**

    curl "http://localhost:9000/v1/tag" \
        -F "imagefile=@/home/ubuntu/Downloads/test1.jpg" \
        -H "Authorization: Bearer ePcfeKIZAQRdAMyWEONpjbYJjE3s3k"

**Image Recognition Request (Remote file):**

    curl "http://localhost:9000/v1/tag" \
        -d "url=https://openzeka.com/static/images/test_image.jpg"  \
        -H "Authorization: Bearer ePcfeKIZAQRdAMyWEONpjbYJjE3s3k"

**Response:**

    {
      "Configuration": {
        "app_name": "first_app",
        "limit": "25000",
        "model": "Model v1",
        "scopes": "api_access",
        "usage": 5
      },
      "Results": [
        {
          "image": "https://openzeka.com/static/images/test_image.jpg",
          "result": {
            "tags": [
              {
                "probability": 98.322,
                "tag": "balloon"
              },
              {
                "probability": 1.656,
                "tag": "parachute"
              },
              {
                "probability": 0.016,
                "tag": "umbrella"
              },
              {
                "probability": 0.002,
                "tag": "airship"
              },
              {
                "probability": 0.001,
                "tag": "lakeside"
              }
            ],
            "time": "0.473"
          },
          "status_code": "OK",
          "status_message": "OK"
        }
      ]
    }


Convert cURL syntax to Python, Node.js, PHP: <http://curl.trillworks.com>