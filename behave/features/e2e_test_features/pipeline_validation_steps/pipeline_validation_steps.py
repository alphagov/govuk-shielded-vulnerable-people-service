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


@given('the data is available for yesterday')
def the_data_is_available_for_yesterday(context):
    '''
    This will always be true. The data is inserted in Yesterday's run since pipeline needs to cut-off data before
    mid night yesterday.
    '''
    pass


@when('the pipeline is processed')
def run_daily_pipeline(context):
    '''
    This will always be true as well. Pipeline is run in staging as part of Gatling stress test.
    '''
    pass


@then('nhs_number "{nhs_number}" is available in LA feed for "{hub}" for yesterday')
def assert_nhs_number_is_available_in_hub(context, nhs_number, hub):
    la_results = get_la_result_for_user(nhs_number, hub)
    assert len(la_results) == 1


@then('nhs_number "{nhs_number}" is available in supermarket feed for yesterday')
def assert_nhs_number_is_available_in_supermarket(context, nhs_number):
    supermarket_results = get_supermarket_result_for_user(nhs_number)
    assert len(supermarket_results) == 1


def get_la_result_for_user(nhs_number, hub):
    la_results = get_latest_la_file_contents(hub)
    print("Using NHS number: {}".format(nhs_number))
    user_results = []
    for result in la_results:
        if result['nhs_number'] == nhs_number and \
                str(date.today() - timedelta(days=1)) in result['submission_datetime']:
            user_results.append(result)
    return user_results


def get_latest_la_file_contents(hub):
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/local_authority/{}/'.format(env, hub)
    print('Prefix is :%s' % (prefix))
    filenames = [obj['Key'] for obj in s3.list_objects(
        Bucket=bucket, Prefix=prefix)['Contents']]

    # find the latest file with GDS-to-LA-Submissions' in filename
    # e.g. web-app-{env}-data/local_authority/Barnsley/2020/10/10/GDS-to-LA-Submissions20200917-162656.csv
    for file in filenames:
        if 'GDS-to-LA-Submissions' in file:
            latest_file = file

    print("Using file: s3://{}/{}".format(bucket, latest_file))
    response = s3.get_object(Bucket=bucket, Key=latest_file)
    lines = response['Body'].read().decode('utf-8').splitlines()
    return csv.DictReader(lines)


def get_supermarket_result_for_user(nhs_number):
    supermarket_results = get_latest_supermarket_file_contents()
    id = hash_nhs_number(nhs_number)
    print("Using NHS number: {} with id: {}".format(nhs_number, id))
    user_results = []
    for result in supermarket_results:
        if result['ID'] == id and \
                str(date.today() - timedelta(days=1)) in result['Timestamp']:
            user_results.append(result)
    return user_results


def get_latest_supermarket_file_contents():
    # get latest file from s3 gds-ons-covid-19-query-results-{env}/web-app-{env}-data/wholesaler/v2
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/supermarket/feed/'.format(env)
    filenames = [obj['Key'] for obj in s3.list_objects(
        Bucket=bucket, Prefix=prefix)['Contents']]

    # find the latest file with 'GDS-to-Supermarkets-Submissions' in filename
    # e.g. web-app-{env}-data/supermarket/feed/GDS-to-Supermarkets-Submissions20200917-162656.csv
    for file in filenames:
        if 'GDS-to-Supermarkets-Submissions' in file:
            latest_file = file

    print("Using file: {}".format(latest_file))
    response = s3.get_object(Bucket=bucket, Key=latest_file)
    lines = response['Body'].read().decode('utf-8').splitlines()
    return csv.DictReader(lines)


def hash_nhs_number(nhs_number):
    m = hashlib.md5()
    salt_concat_nhs_number = salt + ':' + nhs_number
    m.update(salt_concat_nhs_number.encode())
    return m.hexdigest()
