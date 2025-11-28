import os
import time
import unittest

from agentbay import AgentBay
from agentbay.computer import InstalledAppListResult, ProcessListResult
from agentbay.context_sync import ContextSync, SyncPolicy, BWList, WhiteList
from agentbay.api.models import MobileExtraConfig, MobileSimulateMode
from agentbay.exceptions import AgentBayError
from agentbay.model import BoolResult, OperationResult
from agentbay.session_params import CreateSessionParams, ExtraConfigs
from agentbay.mobile import KeyCode, UIElementListResult
from agentbay.mobile_simulate import MobileSimulateService


MOBILE_INFO_MODEL_A = "SM-A505F"
MOBILE_INFO_MODEL_B = "moto g stylus 5G - 2024"

mobile_sim_persistence_context_id = None

class TestMobileSystemIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment by creating a session and initializing ui model.
        """
        api_key = os.getenv(
            "AGENTBAY_API_KEY", "your_api_key"
        )  # Replace with your actual API key
        cls.agent_bay = AgentBay(api_key=api_key)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up test environment.
        """
        pass


    def test_mobile_simulate_for_model_a(self):
        """
        Test device properties after mobile simulate for model a.
        """
        global mobile_sim_persistence_context_id
        # Get a mobile dev info file from DumpSDK or real device library
        print("Upload mobile dev info file...")
        mobile_sim_persistence_context_id = None
        mobile_info_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                "resource", "mobile_info_model_a.json"
        )
        with open(mobile_info_file_path, "r") as f:
            mobile_info_content = f.read()
        
        # Create mobile simulate service and set simulate params
        simulate_service = MobileSimulateService(self.agent_bay)
        simulate_service.set_simulate_enable(True)
        simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
        
        upload_result = simulate_service.upload_mobile_info(mobile_info_content)
        self.assertTrue(upload_result.success, f"Failed to upload mobile dev info file: {upload_result.error_message}")
        mobile_sim_persistence_context_id = upload_result.mobile_simulate_context_id
        print(f"Mobile dev info uploaded successfully: {mobile_sim_persistence_context_id}")

        params = CreateSessionParams(
            image_id="mobile_latest",
            extra_configs=ExtraConfigs(
                mobile=MobileExtraConfig(
                    simulate_config=simulate_service.get_simulate_config()
                )
            )
        )
        result = self.agent_bay.create(params)
        session = None
        self.assertTrue(result.success, "Failed to create session")
        self.assertIsNotNone(result.session, "Session should not be None")
        session = result.session
        print(f"Session created successfully: {session.session_id}")

        # Wait for mobile simulate to complete
        time.sleep(5)
        print("Getting device model after mobile simulate for model a...")
        result = session.command.execute_command("getprop ro.product.model")
        self.assertTrue(result.success, "Failed to get device model")
        model_a_product_model = result.output.strip()
        print(f"Simulated model a mobile product model: {model_a_product_model}")
        self.assertEqual(model_a_product_model, MOBILE_INFO_MODEL_A, f"Device model should be {MOBILE_INFO_MODEL_A}")

        time.sleep(2)
        print("Deleting session...")
        delete_result = self.agent_bay.delete(session)
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")


    def test_mobile_simulate_for_model_b(self):
        """
        Test device properties after mobile simulate for model b.
        """
        # Get a mobile dev info file from DumpSDK or real device library
        print("Upload mobile model b dev info file...")
        mobile_sim_context_id = None
        mobile_info_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                "resource", "mobile_info_model_b.json"
        )
        with open(mobile_info_file_path, "r") as f:
            mobile_info_content = f.read()
        
        # Create mobile simulate service and set simulate params
        simulate_service = MobileSimulateService(self.agent_bay)
        simulate_service.set_simulate_enable(True)
        simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
        
        upload_result = simulate_service.upload_mobile_info(mobile_info_content)
        self.assertTrue(upload_result.success, f"Failed to upload mobile dev info file: {upload_result.error_message}")
        mobile_sim_context_id = upload_result.mobile_simulate_context_id
        print(f"Mobile model b dev info uploaded successfully: {mobile_sim_context_id}")

        params = CreateSessionParams(
            image_id="mobile_latest",
            extra_configs=ExtraConfigs(
                mobile=MobileExtraConfig(
                    simulate_config=simulate_service.get_simulate_config()
                )
            )
        )
        result = self.agent_bay.create(params)
        session = None
        self.assertTrue(result.success, "Failed to create session")
        self.assertIsNotNone(result.session, "Session should not be None")
        session = result.session
        print(f"Session created successfully: {session.session_id}")

        # Wait for mobile simulate to complete
        time.sleep(5)
        print("Getting device model after mobile simulate for model b...")
        result = session.command.execute_command("getprop ro.product.model")
        self.assertTrue(result.success, "Failed to get device model")
        model_b_product_model = result.output.strip()
        print(f"Simulated model b mobile product model: {model_b_product_model}")
        self.assertEqual(model_b_product_model, MOBILE_INFO_MODEL_B, f"Device model should be {MOBILE_INFO_MODEL_B}")

        time.sleep(2)
        print("Deleting session...")
        delete_result = self.agent_bay.delete(session)
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")


    def test_mobile_simulate_persistence(self):
        global mobile_sim_persistence_context_id
        """
        Using model a simulate context to test persistence mobile simulate across sessions.
        """
        # Directly use model a simulate context id to do mobile simulate across sessions.
        # Create mobile simulate service and set simulate params
        simulate_service = MobileSimulateService(self.agent_bay)
        simulate_service.set_simulate_enable(True)
        simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
        simulate_service.set_simulate_context_id(mobile_sim_persistence_context_id)
        
        params = CreateSessionParams(
            image_id="mobile_latest",
            extra_configs=ExtraConfigs(
                mobile=MobileExtraConfig(
                    simulate_config=simulate_service.get_simulate_config()
                )
            )
        )
        result = self.agent_bay.create(params)
        session = None
        self.assertTrue(result.success, "Failed to create session")
        self.assertIsNotNone(result.session, "Session should not be None")
        session = result.session
        print(f"Session created successfully: {session.session_id}")

        # Wait for mobile simulate to complete
        time.sleep(5)
        print("Getting device model after mobile simulate...")
        result = session.command.execute_command("getprop ro.product.model")
        self.assertTrue(result.success, "Failed to get device model")
        persistence_product_model = result.output.strip()
        print(f"Persistent simulated mobile product model: {persistence_product_model}")
        self.assertEqual(persistence_product_model, MOBILE_INFO_MODEL_A, f"Device model should be {MOBILE_INFO_MODEL_A}")

        time.sleep(2)
        print("Deleting session...")
        delete_result = self.agent_bay.delete(session)
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

if __name__ == "__main__":
    unittest.main()
