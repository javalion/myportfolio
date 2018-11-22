import json
import boto3
import StringIO
import zipfile
import mimetypes


def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    portfolioBucket = s3.Bucket('portfolio.terrymckee.com')
    buildBucket = s3.Bucket('portfoliobuild.terrymckee.com')

    portfolio_zip = StringIO.StringIO()
    buildBucket.download_fileobj('portfolio.zip', portfolio_zip)

    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolioBucket.upload_fileobj(obj, nm,
              ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            portfolioBucket.Object(nm).Acl().put(ACL='public-read')
    return 'Hello from Lambda'
