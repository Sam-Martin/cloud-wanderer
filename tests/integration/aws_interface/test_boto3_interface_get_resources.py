import unittest

from cloudwanderer import CloudWandererAWSInterface
from cloudwanderer.exceptions import UnsupportedServiceError

from ..helpers import GenericAssertionHelpers, get_default_mocker
from ..mocks import add_infra


class TestCloudWandererGetResources(unittest.TestCase, GenericAssertionHelpers):
    @classmethod
    def setUpClass(cls):
        cls.enabled_regions = ["eu-west-2", "us-east-1", "ap-east-1"]
        get_default_mocker().start_general_mock(
            restrict_regions=cls.enabled_regions,
            restrict_services=["ec2", "s3", "iam"],
            limit_resources=["ec2:instance", "s3:bucket", "iam:group", "iam:role"],
        )
        add_infra(regions=cls.enabled_regions)

    @classmethod
    def tearDownClass(cls):
        get_default_mocker().stop_general_mock()

    def setUp(self):
        self.aws_interface = CloudWandererAWSInterface()

    def test_get_resources_of_type_in_region_eu_west_2(self):
        result = list(
            self.aws_interface.get_resources(
                service_name="ec2",
                resource_type="instance",
                region="eu-west-2",
            )
        )

        self.assert_dictionary_overlap(result, [{"urn": "urn:aws:.*:eu-west-2:ec2:instance:.*"}])

    def test_get_resources_of_type_in_region_us_east_1(self):
        result = self.aws_interface.get_resources(service_name="ec2", resource_type="instance", region="us-east-1")
        self.assert_dictionary_overlap(result, [{"urn": "urn:aws:.*:us-east-1:ec2:instance:.*"}])

    def test_get_resources_unsupported_service(self):
        with self.assertRaises(UnsupportedServiceError):
            list(self.aws_interface.get_resources(service_name="unicorn_stable", resource_type="instance"))

    def test_get_resources_unsupported_resource_type(self):
        result = list(self.aws_interface.get_resources(service_name="ec2", resource_type="unicorn"))

        assert result == []
