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


@then('nhs_number "{nhs_number}" is available in LA feed for "{hub}" with yesterday date in field "{check_field}"')
def assert_nhs_number_is_available_in_hub(context, nhs_number, hub, check_field):
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/local_authority/{}/'.format(env, hub)
    filename_prefix = 'GDS-to-LA-Submissions'
    id_field = 'nhs_number'
    check_value = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    results = get_result_for_user(bucket, prefix, filename_prefix, id_field, nhs_number, check_field, check_value)
    assert len(results) == 1


@then('nhs_number "{nhs_number}" is available in supermarket feed with yesterday date in field "{check_field}"')
def assert_nhs_number_is_available_in_supermarket(context, nhs_number, check_field):
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/supermarket/feed/'.format(env)
    filename_prefix = 'GDS-to-Supermarkets-Submissions'
    id_field = 'ID'
    id_value = hash_nhs_number(nhs_number)
    check_value = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    results = get_result_for_user(bucket, prefix, filename_prefix, id_field, id_value, check_field, check_value)
    assert len(results) == 1


@then('nhs_number "{nhs_number}" is in churn report for "{hub}" with "{check_value}" in field "{check_field}"')
def assert_nhs_number_is_available_in_hub_churn_report(context, nhs_number, hub, check_field, check_value):
    bucket = 'gds-ons-covid-19-query-results-{}'.format(env)
    prefix = 'web-app-{}-data/local_authority/{}/'.format(env, hub)
    filename_prefix = 'GDS-to-LA-ChurnReport'
    id_field = 'nhs_number'

    results = get_result_for_user(bucket, prefix, filename_prefix, id_field, nhs_number, check_field, check_value)
    assert len(results) == 1


def get_result_for_user(bucket, prefix, filename_prefix, id_field, id_value, check_field, check_value):
    latest_file_content = get_latest_file_contents(bucket, prefix, filename_prefix)
    print("Using {}: {}".format(id_field, id_value))
    print("Checking field {}: {}".format(check_field, check_value))

    user_results = []
    for record in latest_file_content:
        if record[id_field] == id_value and check_value in record[check_field]:
            user_results.append(record)
    return user_results


def get_latest_file_contents(bucket, prefix, filename_prefix):
    print('Prefix is :%s' % (prefix))
    paginator = s3.get_paginator('list_objects_v2')
    bucket_items = paginator.paginate(Bucket=bucket, Prefix=prefix)

    filenames =[]
    for item in bucket_items:
        for object in item['Contents']:
            filenames.append(object['Key'])

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
