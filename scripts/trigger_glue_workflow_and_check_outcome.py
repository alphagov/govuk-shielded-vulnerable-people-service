import boto3
import json
import time
from datetime import datetime, timezone
import logging
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--workflow_to_trigger", help="workflow to trigger")
parser.add_argument("--workflows_to_check", help="comma separted list of workflows to check")
parser.add_argument("--timeout", help="timeout, in seconds", type=int)
parser.add_argument("--wait_time", help="time to wait before checking the status again in seconds", type=int)
args = parser.parse_args()

if (
    args.workflow_to_trigger is None or
    args.workflows_to_check is None or
    args.timeout is None or
    args.wait_time is None
   ):
    raise Exception('''Please supply arguments for:
                         --workflow_to_trigger
                         --workflows_to_check
                         --timeout
                         --wait_time''')


workflow_to_trigger = args.workflow_to_trigger
workflows_to_check = args.workflows_to_check.split(',')
running_statuses = ['RUNNING', 'STOPPING']
completed_statues = ['COMPLETED', 'STOPPED', 'ERROR']
timeout = args.timeout
wait_time = args.wait_time

client = boto3.client('glue')
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

started_date = datetime.now(timezone.utc)


def check_work_flow_compeleted(work_flow_name):

    while True:
        work_flow_dict = client.get_workflow(Name=work_flow_name)
        if work_flow_dict['Workflow']['LastRun']['StartedOn'] > started_date:
            logger.info(f'WorkFlow: {work_flow_name}, Started')
            break

        if (datetime.now(timezone.utc) - started_date).total_seconds() > timeout:
            logger.error(f'Error Timeout Workflow: {work_flow_name}')
            raise Exception(f'Timeout. Workflow {work_flow_name}, ran for longer than expected')
        logger.info(f'WorkFlow: {work_flow_name}, Waiting for workflow to start')
        time.sleep(wait_time)

    while True:
        work_flow_dict = client.get_workflow(Name=work_flow_name)
        status = work_flow_dict['Workflow']['LastRun']['Status']

        if status in completed_statues:
            if(status == 'COMPLETED'):
                logger.info(
                    f'Workflow:{work_flow_name}, Status:{status}')
            else:
                logger.error(
                    f'Workflow:{work_flow_name}, Status:{status}')
            break

        if (datetime.now(timezone.utc) - started_date).total_seconds() > timeout:
            logger.error('Error Timeout Workflow: ' + work_flow_name)
            raise Exception('Timeout. Workflow ran for longer than expected')
        logger.info(f'WorkFlow: {work_flow_name}, Status: {status}, Waiting for workflow to complete')
        time.sleep(wait_time)

    work_stats = work_flow_dict['Workflow']['LastRun']['Statistics']

    if (
        int(work_stats['TimeoutActions']) > 0 or
        int(work_stats['FailedActions']) > 0 or
        int(work_stats['StoppedActions']) > 0 or
        int(work_stats['RunningActions']) > 0 or
        int(work_stats['TotalActions']) != int(work_stats['SucceededActions'])
    ):
        error_message = 'Error not all jobs completed successfully, WorkFlow:'
        error_message += work_flow_name + os.linesep + \
            json.dumps(work_stats, indent=4, sort_keys=True)
        logger.error(error_message)
        raise Exception(error_message)
    else:
        logger.info(f'Workflow:{work_flow_name}, all jobs completed successfully')


def main():
    logger.info(f'Triggering Workflow:{workflow_to_trigger}')
    client.start_workflow_run(Name=workflow_to_trigger)

    for workflow in workflows_to_check:
        check_work_flow_compeleted(workflow)

    logger.info('All workflows completed successfully')


main()
