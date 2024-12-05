from unittest import TestCase

from gateway.memory_repository_gateway import MemoryRepositoryGateway

class MemoryRepositoryGatewayTest(TestCase):

    def setUp(self):

        return super().setUp()

    def test_gateway_creates_repository(self):
        MemoryRepositoryGateway().create_repository()
