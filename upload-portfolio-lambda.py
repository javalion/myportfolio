import json
import boto3
import StringIO
import zipfile
import mimetypes


def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    s3Client = boto3.client('sns',region_name='us-east-1')

    location = {
        "bucketName": 'portfoliobuild.terrymckee.com',
        "objectKey": 'portfolio.zip'
    }

    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print "Building portfolio from " + str(location)
        portfolioBucket = s3.Bucket('portfolio.terrymckee.com')
        buildBucket = s3.Bucket(location["bucketName"])

        portfolio_zip = StringIO.StringIO()
        buildBucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolioBucket.upload_fileobj(obj, nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolioBucket.Object(nm).Acl().put(ACL='public-read')
        s3Client.publish(TopicArn='arn:aws:sns:us-east-1:828873072107:displayPortfolioTopic', Message='Portfolio deployed successfully.', Subject='Portfolio Deployed')
        if job:
            codePipeline = boto3.client('codepipeline')
            codePipeline.put_job_success_result(jobId=job["id"])
    except:
        s3Client.publish(TopicArn='arn:aws:sns:us-east-1:828873072107:displayPortfolioTopic', Message='Portfolio NOT deployed.', Subject='Portfolio Deployment Failed')
        raise
    return 'Hello from Lambda'
