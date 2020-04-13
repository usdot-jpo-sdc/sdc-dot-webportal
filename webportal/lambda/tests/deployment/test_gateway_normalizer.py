from deployment import gateway_normalizer, chalice_config_reader
import os
import boto3
import pytest
from botocore.stub import Stubber


TEST_ENVIRONMENT = 'some_environment'
REST_API_ID = 'some_rest_api_id'
API_GATEWAY_STAGE = 'some_api_stage'
MOCK_ACCOUNT_NUMBER = 42
MOCK_DEPLOYED_GATEWAY = {"rest_api_id": REST_API_ID}
MOCK_CHALICE_CONFIG = {
    "stages": {
        TEST_ENVIRONMENT: {
            "api_gateway_stage": API_GATEWAY_STAGE
        }
    }
}


@pytest.fixture
def api_gateway_client():
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    api_gateway_client = boto3.client('apigateway')
    return api_gateway_client


@pytest.fixture
def api_gateway_stubber(api_gateway_client):
    return Stubber(api_gateway_client)


@pytest.fixture
def mock_chalice_config_reader(mocker):
    mocker.patch.object(chalice_config_reader, 'find_deployed_config')
    chalice_config_reader.find_deployed_config.return_value = MOCK_DEPLOYED_GATEWAY
    mocker.patch.object(chalice_config_reader, 'chalice_config')
    chalice_config_reader.chalice_config.return_value = MOCK_CHALICE_CONFIG
    return chalice_config_reader


@pytest.fixture
def partially_mocked_gateway_normalizer(mocker, api_gateway_client):
    mocker.patch.object(gateway_normalizer, 'api_gateway_client')
    gateway_normalizer.api_gateway_client.return_value = api_gateway_client
    mocker.patch.object(gateway_normalizer, 'get_region')
    gateway_normalizer.get_region.return_value = 'us-east-1'
    mocker.patch.object(gateway_normalizer, 'get_account_number')
    gateway_normalizer.get_account_number.return_value = MOCK_ACCOUNT_NUMBER
    return gateway_normalizer


def test_normalize_gateway_sets_name_and_stage_logging_and_adds_tags(mock_chalice_config_reader, partially_mocked_gateway_normalizer, api_gateway_stubber):
    environment = 'some_environment'
    api_gateway_stubber.add_response('update_rest_api', {}, {'restApiId': REST_API_ID,
                                                             'patchOperations': [{'op': 'replace', 'path': '/name', 'value': f'{environment}-webportal'},
                                                                                 {'op': 'replace', 'path': '/description', 'value': f'{environment}-webportal'}]})
    api_gateway_stubber.add_response('update_stage', {}, {'restApiId': REST_API_ID, 'stageName': API_GATEWAY_STAGE,
                                                             'patchOperations': [{'op': 'replace', 'path': '/accessLogSettings/destinationArn',
                                                                                  'value': f'arn:aws:logs:us-east-1:{MOCK_ACCOUNT_NUMBER}:log-group:/aws/apigateway/{REST_API_ID}/{API_GATEWAY_STAGE}'},
                                                                                  {'op': 'replace', 'path': '/accessLogSettings/format', 'value': gateway_normalizer.LOG_FORMAT}]})
    api_gateway_stubber.add_response('tag_resource', {}, {'resourceArn': f'arn:aws:apigateway:us-east-1::/restapis/{REST_API_ID}',
                                                          "tags": {"Environment": environment, "Project": "SDC-Platform", "Team": "sdc-platform"}})

    with api_gateway_stubber:
        partially_mocked_gateway_normalizer.normalize_gateway(environment)

        api_gateway_stubber.assert_no_pending_responses()
        chalice_config_reader.find_deployed_config.assert_called_with('rest_api', environment)
        chalice_config_reader.chalice_config.assert_called_with()



def test_api_gateway_client_returns_api_gateway_client():
    result_class = gateway_normalizer.api_gateway_client()

    assert 'botocore.client.APIGateway' == f'{result_class.__class__.__module__}.{result_class.__class__.__name__}'


def test_get_region_returns_region():
    region = os.popen('aws configure get region').read().strip()

    assert region == gateway_normalizer.get_region()