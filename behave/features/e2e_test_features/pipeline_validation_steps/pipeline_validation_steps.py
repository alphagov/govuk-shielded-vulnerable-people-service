from behave import given, when, then

import boto3
from datetime import timedelta, date
import csv
import hashlib
import os

env = os.environ['ENVIRONMENT']
salt = os.environ['SALT']
region = os.environ['REGION']

s3 = boto3.client('s3')
glue_client = boto3.client('glue', region_name=region)


@given('there was a new web submission yesterday')
def the_data_is_available_for_yesterday(context):
    '''
    This will always be true. The data is inserted in Yesterday's run since pipeline needs to cut-off data before
    mid night yesterday.
    '''
    pass


@when('the pipeline has completed successfully')
def run_daily_pipeline(context):
    '''
    This will always be true as well. Pipeline is run in staging as part of Daily pipeline and MI execution test.
    '''
    pass


@then('nhs_number "{nhs_number}" is available in LA feed for "{hub}" for yesterday')
def assert_nhs_number_is_available_in_hub(context, nhs_number, hub):
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/local_authority/{}/'.format(env, hub)
    filename_prefix = 'GDS-to-LA-Submissions'
    id_field = 'nhs_number'
    timestamp_field = 'submission_datetime'

    la_results = get_result_for_user(nhs_number, id_field, bucket, prefix, filename_prefix, timestamp_field)
    assert len(la_results) == 1


@then('nhs_number "{nhs_number}" is available in supermarket feed for yesterday')
def assert_nhs_number_is_available_in_supermarket(context, nhs_number):
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/supermarket/feed/'.format(env)
    filename_prefix = 'GDS-to-Supermarkets-Submissions'
    id_field = 'ID'
    timestamp_field = 'Timestamp'
    id = hash_nhs_number(nhs_number)

    la_results = get_result_for_user(id, id_field, bucket, prefix, filename_prefix, timestamp_field)
    assert len(la_results) == 1


def get_result_for_user(id, id_field, bucket, prefix, filename_prefix, timestamp_field):
    la_results = get_latest_file_contents(bucket, prefix, filename_prefix)
    print("Using {}: {}".format(id_field, id))

    date_stamp = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    print("Checking timestamp {}".format(date_stamp))

    user_results = []
    for result in la_results:
        if result[id_field] == id and date_stamp in result[timestamp_field]:
            user_results.append(result)
    return user_results


def get_latest_file_contents(bucket, prefix, filename_prefix):
    print('Prefix is :%s' % (prefix))
    filenames = [obj['Key'] for obj in s3.list_objects_v2(
        Bucket=bucket, Prefix=prefix)['Contents']]

    # find the latest file with filename prefix in filename
    # e.g. web-app-{env}-data/local_authority/Barnsley/2020/10/10/GDS-to-LA-Submissions20200917-162656.csv
    # e.g. web-app-{env}-data/supermarket/feed/GDS-to-Supermarkets-Submissions20200917-162656.csv
    for file in filenames:
        if filename_prefix in file:
            latest_file = file

    print("Using file: s3://{}/{}".format(bucket, latest_file))
    response = s3.get_object(Bucket=bucket, Key=latest_file)
    lines = response['Body'].read().decode('utf-8').splitlines()
    return csv.DictReader(lines)


def hash_nhs_number(nhs_number):
    m = hashlib.md5()
    salt_concat_nhs_number = salt + ':' + nhs_number
    m.update(salt_concat_nhs_number.encode())
    return m.hexdigest()
