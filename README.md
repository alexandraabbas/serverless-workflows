# Serverless Workflow Management (WIP)

Source code for "Creating a fully serverless workflow management platform" ServerlessDays talk.

## Concept

## Setup

### Create resources

Create the following resources in Google Cloud in order to run this project.

* Create a Google Cloud project
* Create a Cloud Storage bucket
* Create 3 "folders" _called landing_, _processing_ and _backup_ in your Cloud Storage bucket

Take note of your project ID, bukcet name and region as we're going to use these later. Alternatively export these variables as environment variables.

```bash
export PROJECT=<your-project-name>
export BUCKET=<your-bucket-name>
export REGION=<your-bucket-region>
```
Set the project that you just created as your default project using the gcloud command line tool.

```bash
gcloud config set project ${PROJECT}
```

### Enable APIs

Run the following command to enable Cloud Functions, Workflows, Cloud Build and Cloud Storage APIs.

```bash
gcloud services enable \
    cloudfunctions.googleapis.com \
    workflows.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com
```

## Deploy Cloud Functions

This repository includes 3 Cloud Functions. These functions contain the business logic corresponding to steps in our workflow.

* `list_files`: Lists file names in a bucket or in a "folder" of a bucket
* `move_files`: Renames prefixes of objects in a bucket (moves object from one "folder" to another in a bucket)
* `load_files`: Loads files from Cloud Storage into a BigQuery table

Each function has its own directory. Change to that directory and deploy each function using the following command.

```bash
cd list_files/
gcloud functions deploy list_files \
    --runtime python37 \
    --trigger-http \
    --allow-unauthenticated \
    --region ${REGION}
```
Run the same command for each function.

## Deploy workflows



```bash
gcloud beta workflows deploy bigquery_data_load \
    --source=bigquery_data_load.yaml \
    --region ${REGION}
```

## Schedule workflows

### Create Service Account for Cloud Scheduler

Let's create a Service Account for Cloud Scheduler which will be responsible for triggering workflows.

```bash
export SERVICE_ACCOUNT=scheduler-sa
gcloud iam service-accounts create ${SERVICE_ACCOUNT}
gcloud projects add-iam-policy-binding ${PROJECT} \
    --member "serviceAccount:${SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com" \
    --role "roles/workflows.invoker"
```

### Create Cloud Scheduler job

Let's create a job in Cloud Scheduler which will trigger our workflow once every hour. This job will use the service account we've just created. We also specify a request body which will contain input arguments for our workflow.

```bash
gcloud scheduler jobs create http bigquery_data_load_hourly \
    --schedule="0 * * * *" \
    --uri="https://workflowexecutions.googleapis.com/v1beta/projects/${PROJECT}/locations/${REGION}/workflows/bigquery_data_load/executions" \
    --oauth-service-account-email="${SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com" \
    --message-body='{"bucket":"$BUCKET","project":"${PROJECT}","region":"${REGION}"}'
```

## Monitor workflows

You can monitor your workflows via Google Cloud Consolse. Unfortunately Google Cloud Console doesn't generate any visual graph of your workflows yet. You can assess all logs in Workflows and Cloud Functions UI, these logs allow you to configure metrics, alerts and build monitoring bashboards.
