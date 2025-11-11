---
title: "ADR-0001: Azure Deployment Strategy for Glasgow Workshop Flask Application"
status: "Proposed"
date: "2025-11-11"
authors: "DevOps Team, Platform Engineering"
tags: ["architecture", "decision", "deployment", "azure", "flask", "infrastructure"]
supersedes: ""
superseded_by: ""
---

## Status

**Proposed**

## Context

The Glasgow Workshop is a Python-based Flask web application designed for learning GitHub Copilot capabilities. The application displays interactive maps of Glasgow using Folium and integrates geospatial data from the City of Glasgow's open data portal. As part of the workshop experience, the application needs to be deployed to a cloud environment where participants can access it remotely and experience real-world deployment scenarios.

The application has the following technical characteristics:
- **Technology Stack**: Python 3.9+, Flask web framework, Folium for map visualization
- **Data Requirements**: Fetches and displays GeoJSON data from Glasgow's open data portal
- **User Base**: Workshop participants, educators, and learners
- **Scale**: Low to medium traffic, primarily for educational purposes
- **Development Approach**: Rapid iteration and experimentation-focused

Key constraints and requirements include:
- Must be simple enough for workshop participants to understand and potentially replicate
- Should support rapid deployments for iterative development during workshops
- Needs to be cost-effective for an educational/workshop context
- Should align with modern cloud-native best practices
- Must support Python 3.9+ runtime environments
- Should provide good logging and monitoring capabilities for debugging during workshops

The decision requires selecting an appropriate Azure service and deployment approach that balances simplicity, cost, and production-ready practices.

## Decision

We will deploy the Glasgow Workshop Flask application to **Azure App Service** using a containerized approach with **Azure Container Registry (ACR)** and implement CI/CD through **GitHub Actions**.

**Deployment Architecture:**

1. **Primary Hosting**: Azure App Service for Containers (Web App for Containers)
   - Linux-based App Service Plan (B1 or S1 tier for workshop use)
   - Python 3.11+ runtime via Docker container
   - Gunicorn as WSGI server (not Flask development server)

2. **Container Management**:
   - Docker containerization for consistency across environments
   - Azure Container Registry (ACR) for private container image storage
   - Managed identity authentication between App Service and ACR

3. **CI/CD Pipeline**:
   - GitHub Actions workflow for automated builds and deployments
   - Triggered on pushes to main branch and manual workflow dispatch
   - Multi-stage process: build → test → containerize → push to ACR → deploy to App Service

4. **Configuration Management**:
   - Environment variables stored in Azure App Service Configuration
   - Application Insights for monitoring and diagnostics
   - Azure Key Vault for sensitive configuration (if needed in future)

**Rationale:**
- **Container approach** provides consistency between development and production environments
- **Azure App Service** offers fully managed infrastructure with automatic scaling and high availability
- **GitHub Actions** integration enables seamless CI/CD from the existing GitHub repository
- This architecture is educational yet production-grade, teaching participants industry best practices
- Managed services reduce operational overhead while maintaining flexibility

## Consequences

### Positive

- **POS-001**: **Simplified Operations** - Azure App Service provides a fully managed platform that handles infrastructure management, OS patching, and runtime updates automatically, reducing operational burden
- **POS-002**: **Container Consistency** - Docker containerization ensures identical behavior across development, testing, and production environments, eliminating "works on my machine" issues
- **POS-003**: **Educational Value** - The architecture uses industry-standard tools (Docker, CI/CD, managed services) that workshop participants can apply in their own projects
- **POS-004**: **Rapid Deployment Capability** - GitHub Actions CI/CD enables quick iterations during workshops, with automated deployments taking typically 3-5 minutes from code commit to live update
- **POS-005**: **Built-in Monitoring** - Integration with Azure Monitor and Application Insights provides real-time visibility into application performance, errors, and usage patterns
- **POS-006**: **Scalability Ready** - App Service supports both vertical and horizontal scaling, allowing the application to handle increased load during popular workshops
- **POS-007**: **Cost Control** - Starting with B1 tier (~$13/month) provides adequate resources for workshops while keeping costs predictable and low

### Negative

- **NEG-001**: **Azure Lock-in** - The solution is tightly coupled to Azure services, making migration to other cloud providers require significant rearchitecture
- **NEG-002**: **Container Overhead** - Adding Docker and container registry introduces additional complexity compared to direct code deployment via `az webapp up`
- **NEG-003**: **Learning Curve** - Workshop participants need to understand Docker, ACR, and CI/CD concepts in addition to Flask development
- **NEG-004**: **Cold Start Latency** - App Service containers may experience cold start delays (5-10 seconds) after periods of inactivity on lower-tier plans
- **NEG-005**: **Regional Limitations** - App Service availability and features vary by Azure region, potentially limiting deployment location choices
- **NEG-006**: **Debugging Complexity** - Issues in containerized environments can be harder to diagnose compared to direct Python deployments

## Alternatives Considered

### Alternative 1: Direct Deployment with az webapp up

- **ALT-001**: **Description**: Deploy Flask application directly to Azure App Service using the Azure CLI command `az webapp up`, which automatically provisions resources and deploys code without containers
- **ALT-002**: **Rejection Reason**: While simpler for initial deployment, this approach lacks environment consistency guarantees and makes it harder to reproduce deployments reliably. The direct deployment method also doesn't teach participants about containerization, which is increasingly important in modern development workflows. Additionally, managing dependencies and runtime configuration is less explicit without a Dockerfile.

### Alternative 2: Azure Container Instances (ACI)

- **ALT-003**: **Description**: Deploy the containerized application using Azure Container Instances, which provides on-demand container hosting without managing App Service Plans
- **ALT-004**: **Rejection Reason**: ACI is optimized for batch jobs and short-lived tasks rather than long-running web applications. It lacks built-in features like automatic SSL certificates, custom domain management, and integrated deployment slots that are valuable for web hosting. ACI also requires additional networking configuration (Azure Virtual Network integration) to provide reliable public access, adding complexity.

### Alternative 3: Azure Kubernetes Service (AKS)

- **ALT-005**: **Description**: Deploy the application to a fully managed Kubernetes cluster using Azure Kubernetes Service, providing maximum flexibility and orchestration capabilities
- **ALT-006**: **Rejection Reason**: AKS introduces significant operational complexity and higher costs that are unnecessary for a single containerized web application. The learning curve for Kubernetes would distract from the workshop's focus on GitHub Copilot and Flask development. AKS is better suited for microservices architectures and applications requiring advanced orchestration features. Minimum viable AKS cluster costs ~$150/month, far exceeding the workshop budget requirements.

### Alternative 4: Azure Functions (Serverless)

- **ALT-007**: **Description**: Refactor the Flask application to run as Azure Functions using HTTP triggers, adopting a serverless architecture
- **ALT-008**: **Rejection Reason**: Azure Functions have execution time limits (10 minutes on Consumption plan) and are optimized for event-driven, stateless workloads. The Flask application structure would require significant refactoring to fit the Functions programming model. Additionally, serving Folium map visualizations and handling geospatial data processing is better suited to a traditional web application architecture. Functions also introduce complexity around state management and session handling.

### Alternative 5: Static Azure Storage with Azure Functions Backend

- **ALT-009**: **Description**: Serve the Flask application's frontend from Azure Storage static website hosting and implement backend API endpoints as Azure Functions
- **ALT-010**: **Rejection Reason**: This approach would require completely restructuring the application to separate frontend and backend, introducing significant development effort for minimal benefit in a workshop context. Flask's integrated rendering capabilities would be underutilized. The added complexity of managing two separate deployment targets contradicts the goal of keeping the solution straightforward for educational purposes.

## Implementation Notes

- **IMP-001**: **Dockerfile Requirements** - Create a production-ready Dockerfile using Python 3.11+ base image, installing dependencies from requirements.txt, and using Gunicorn as the WSGI server. Set appropriate environment variables and expose port 8000. Example: `FROM python:3.11-slim`, `WORKDIR /app`, `COPY requirements.txt .`, `RUN pip install -r requirements.txt`, `COPY . .`, `EXPOSE 8000`, `CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]`

- **IMP-002**: **GitHub Actions Workflow** - Implement a CI/CD workflow file (`.github/workflows/azure-deploy.yml`) with the following stages: (1) Checkout code, (2) Log in to Azure using service principal credentials stored in GitHub secrets, (3) Build Docker image, (4) Push image to Azure Container Registry, (5) Deploy to Azure App Service using the updated container image. Use environment-specific workflows for staging and production if needed.

- **IMP-003**: **Azure Resource Provisioning** - Create necessary Azure resources using Azure CLI or Azure Portal: (1) Resource Group for logical grouping, (2) Azure Container Registry with Basic SKU, (3) App Service Plan with Linux OS and B1 tier (can scale up as needed), (4) App Service (Web App) configured for container deployment with system-assigned managed identity enabled for ACR access. Document resource naming conventions (e.g., `glasgow-workshop-<environment>-<resource-type>`).

- **IMP-004**: **Environment Configuration** - Store all environment-specific configuration in Azure App Service Configuration settings, not in code or Dockerfile. Include variables like `FLASK_ENV`, `LOG_LEVEL`, and any API keys for external data sources. Use Azure Key Vault references for sensitive values. Enable Application Insights and set `APPLICATIONINSIGHTS_CONNECTION_STRING`.

- **IMP-005**: **Monitoring and Logging** - Configure Application Insights for comprehensive monitoring including request telemetry, dependency tracking, and exception logging. Set up App Service diagnostic logging (application and web server logs) with retention policies. Create Azure Monitor alerts for critical metrics such as HTTP 5xx errors exceeding thresholds and high response times.

- **IMP-006**: **Health Checks and Reliability** - Implement a `/health` endpoint in Flask that returns 200 OK when the application is healthy. Configure App Service health check feature to monitor this endpoint. Set up deployment slots (staging/production) for zero-downtime deployments during workshops if budget allows.

- **IMP-007**: **Initial Deployment Steps** - (1) Test locally with Docker: `docker build -t glasgow-workshop:local .` and `docker run -p 8000:8000 glasgow-workshop:local`, (2) Create Azure resources using provided scripts or manual steps, (3) Configure GitHub secrets for Azure credentials, (4) Push code to trigger GitHub Actions deployment, (5) Verify deployment by accessing the App Service URL, (6) Configure custom domain and SSL certificate if needed.

- **IMP-008**: **Cost Optimization** - Start with B1 tier App Service Plan (~$13/month) for development and workshops. Use auto-stop policies to shut down non-production environments outside workshop hours. Monitor Azure Cost Management dashboard regularly. Consider switching to Consumption-based App Service Plan if usage patterns are very intermittent.

- **IMP-009**: **Rollback Strategy** - Maintain previous container image tags in ACR. In case of deployment issues, quickly rollback by updating App Service container settings to point to the last known good image version. Use GitHub Actions workflow with manual approval step for production deployments to enable pre-deployment validation.

- **IMP-010**: **Documentation and Knowledge Transfer** - Create deployment runbook documentation in repository (`docs/deployment/azure-setup.md`) covering: resource provisioning steps, GitHub secrets configuration, deployment workflow trigger process, troubleshooting common issues, and cost monitoring guidance. Include architecture diagrams showing data flow and resource relationships.

## References

- **REF-001**: [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/) - Official Microsoft documentation for Azure App Service features and capabilities
- **REF-002**: [Deploy a Python Web App to Azure App Service Quickstart](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python) - Step-by-step guide for Python application deployment
- **REF-003**: [Containerize Python Apps for Azure App Service](https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app-for-app-service) - Tutorial on containerizing Python applications for Azure
- **REF-004**: [GitHub Actions for Azure](https://docs.github.com/en/actions/deployment/deploying-to-your-cloud-provider/deploying-to-azure) - Documentation on setting up CI/CD pipelines with GitHub Actions for Azure deployments
- **REF-005**: [Azure Container Registry Documentation](https://learn.microsoft.com/en-us/azure/container-registry/) - Guide to working with Azure Container Registry
- **REF-006**: [Azure App Service Best Practices](https://learn.microsoft.com/en-us/azure/app-service/app-service-best-practices) - Production deployment best practices and recommendations
- **REF-007**: [Flask Deployment Documentation](https://flask.palletsprojects.com/en/latest/deploying/) - Flask framework official deployment guidance including Gunicorn configuration
- **REF-008**: [Application Insights for Python Applications](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python) - Monitoring and telemetry setup for Python applications in Azure
