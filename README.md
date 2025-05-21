# MiniTasks - Cloud-Native App

## Overview
MiniTasks is a cloud-native application built with Flask, deployed on Google Cloud Platform (GCP) using Kubernetes. It demonstrates best practices for building, deploying, and scaling microservices in a cloud environment.

## Prerequisites
- Python 3.8 or higher
- Google Cloud SDK
- kubectl
- Docker
- Terraform (optional, for infrastructure as code)
- A GCP account with billing enabled
- Required GCP APIs enabled:
  - Compute Engine
  - Kubernetes Engine
  - Cloud Build
  - Artifact Registry
  - Pub/Sub
  - Cloud Functions
  - Cloud Storage
  - IAM
  - Cloud Resource Manager

## Deployment Steps
### Local Development
1. Clone the repository
   ```
   git clone https://github.com/muhammadIsHere/miniTask.git
   cd miniTask
   ```

2. Set up a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r app/requirements.txt
   ```

4. Run the Flask application locally
   ```
   python app/app.py
   ```

### GCP Deployment
1. Build and push the Docker image
   ```
   # Commands will be provided
   ```

2. Deploy to GKE
   ```
   # Commands will be provided
   ```

3. Set up Cloud Functions
   ```
   # Commands will be provided
   ```

## Running Tests
### Unit Tests
```
python -m pytest tests/unit
```

### Integration Tests
```
python -m pytest tests/integration
```

### Performance Tests (Locust)
```
cd tests/locust
locust -f locustfile.py
```
Then access the Locust web interface at http://localhost:8089.

## Architecture
```
[Architecture diagram to be added]
```

The application follows a microservices architecture with the following components:
- Flask web application
- Kubernetes for orchestration
- Cloud Functions for asynchronous processing
- Pub/Sub for messaging
- Cloud Storage for file storage

## Cost Considerations
- GKE cluster costs: ~$XX/month (depends on node size and count)
- Cloud Functions: Pay per invocation
- Cloud Storage: Pay per GB stored
- Pub/Sub: Pay per message
- Network egress: Charges apply for data leaving GCP

Consider setting up billing alerts and using GCP's cost calculator to estimate monthly expenses before deployment.

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 