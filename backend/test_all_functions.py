import asyncio
import sys
import uuid
import json
from pathlib import Path
from ulid import ULID

from sentient_agent_framework.interface.session import SessionObject
from sentient_agent_framework.interface.request import Query
from agent.provenance_guardian import ProvenanceGuardian
from agent.fingerprint_service import FingerprintService
from fingerprints.storage import FingerprintStorage
from fingerprints.validator import FingerprintValidator
from api.routes import SSEResponseHandler
from utils.logger import get_logger

logger = get_logger(__name__)


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_result(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        for test in self.tests:
            status = "✅ PASS" if test["passed"] else "❌ FAIL"
            print(f"{status} | {test['name']}")
            if test["details"]:
                print(f"      {test['details']}")
        print("="*60)
        print(f"Total: {len(self.tests)} | Passed: {self.passed} | Failed: {self.failed}")
        print("="*60)


results = TestResults()


async def test_agent_initialization():
    """Test 1: Agent Initialization"""
    print("\n🧪 Test 1: Agent Initialization")
    try:
        agent = ProvenanceGuardian()
        results.add_result(
            "Agent Initialization",
            True,
            "Agent created successfully"
        )
        return agent
    except Exception as e:
        results.add_result(
            "Agent Initialization",
            False,
            f"Error: {str(e)}"
        )
        return None


async def test_help_command(agent: ProvenanceGuardian):
    """Test 2: Help Command"""
    print("\n🧪 Test 2: Help Command")
    try:
        session = SessionObject(
            session_id="test-help",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        query = Query(id=str(ULID()), prompt="help")
        handler = SSEResponseHandler()
        
        await agent.assist(session, query, handler)
        
        if len(handler.events) > 0:
            has_help_content = any(
                "Provenance Guardian Commands" in str(event.get('content', ''))
                for event in handler.events
                if event.get('type') == 'text_block'
            )
            
            results.add_result(
                "Help Command",
                has_help_content,
                f"Received {len(handler.events)} events"
            )
        else:
            results.add_result(
                "Help Command",
                False,
                "No events received"
            )
    except Exception as e:
        results.add_result(
            "Help Command",
            False,
            f"Error: {str(e)}"
        )


async def test_self_verification(agent: ProvenanceGuardian):
    """Test 3: Self-Verification"""
    print("\n🧪 Test 3: Self-Verification")
    try:
        session = SessionObject(
            session_id="test-verify",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        query = Query(id=str(ULID()), prompt="verify yourself")
        handler = SSEResponseHandler()
        
        await agent.assist(session, query, handler)
        
        has_verification = any(
            event.get('event_type') == 'SELF_VERIFICATION'
            for event in handler.events
        )
        
        results.add_result(
            "Self-Verification",
            has_verification,
            f"Received {len(handler.events)} events"
        )
    except Exception as e:
        results.add_result(
            "Self-Verification",
            False,
            f"Error: {str(e)}"
        )


async def test_fingerprint_generation(agent: ProvenanceGuardian):
    """Test 4: Fingerprint Generation"""
    print("\n🧪 Test 4: Fingerprint Generation")
    try:
        session = SessionObject(
            session_id="test-gen",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        query = Query(id=str(ULID()), prompt="generate fingerprints for me")
        handler = SSEResponseHandler()
        
        await agent.assist(session, query, handler)
        
        fingerprint_event = None
        for event in handler.events:
            if event.get('event_type') == 'FINGERPRINTS':
                fingerprint_event = event
                break
        
        if fingerprint_event:
            data = fingerprint_event.get('data', {})
            has_queries = 'queries' in data
            has_responses = 'responses' in data
            
            results.add_result(
                "Fingerprint Generation",
                has_queries and has_responses,
                f"Generated {len(data.get('queries', []))} fingerprints"
            )
        else:
            results.add_result(
                "Fingerprint Generation",
                False,
                "No fingerprint event found"
            )
    except Exception as e:
        results.add_result(
            "Fingerprint Generation",
            False,
            f"Error: {str(e)}"
        )


async def test_fingerprint_guide(agent: ProvenanceGuardian):
    """Test 5: Fingerprinting Guide"""
    print("\n🧪 Test 5: Fingerprinting Guide")
    try:
        session = SessionObject(
            session_id="test-guide",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        query = Query(id=str(ULID()), prompt="how do I fingerprint my model?")
        handler = SSEResponseHandler()
        
        await agent.assist(session, query, handler)
        
        has_guide = any(
            event.get('event_type') == 'GUIDE'
            for event in handler.events
        )
        
        results.add_result(
            "Fingerprinting Guide",
            has_guide,
            f"Received {len(handler.events)} events"
        )
    except Exception as e:
        results.add_result(
            "Fingerprinting Guide",
            False,
            f"Error: {str(e)}"
        )


async def test_unknown_command(agent: ProvenanceGuardian):
    """Test 6: Unknown Command Handling"""
    print("\n🧪 Test 6: Unknown Command Handling")
    try:
        session = SessionObject(
            session_id="test-unknown",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        query = Query(id=str(ULID()), prompt="this is a random unknown command")
        handler = SSEResponseHandler()
        
        await agent.assist(session, query, handler)
        
        has_response = len(handler.events) > 0
        
        results.add_result(
            "Unknown Command Handling",
            has_response,
            "Agent handled unknown command gracefully"
        )
    except Exception as e:
        results.add_result(
            "Unknown Command Handling",
            False,
            f"Error: {str(e)}"
        )


def test_fingerprint_service():
    """Test 7: Fingerprint Service"""
    print("\n🧪 Test 7: Fingerprint Service")
    try:
        service = FingerprintService()
        guide = service.get_setup_guide()
        has_steps = 'steps' in guide
        has_tips = 'tips' in guide
        
        results.add_result(
            "Fingerprint Service - Guide",
            has_steps and has_tips,
            f"Guide has {len(guide.get('steps', []))} steps"
        )
    except Exception as e:
        results.add_result(
            "Fingerprint Service - Guide",
            False,
            f"Error: {str(e)}"
        )


async def test_fingerprint_generation_direct():
    """Test 8: Direct Fingerprint Generation"""
    print("\n🧪 Test 8: Direct Fingerprint Generation")
    try:
        service = FingerprintService()
        
        fingerprints = await service.generate_fingerprints(
            num_fingerprints=10,
            key_length=5,
            response_length=5
        )
        
        has_correct_count = len(fingerprints['queries']) == 10
        has_responses = len(fingerprints['responses']) == 10
        has_metadata = 'metadata' in fingerprints
        
        results.add_result(
            "Direct Fingerprint Generation",
            has_correct_count and has_responses and has_metadata,
            f"Generated {len(fingerprints['queries'])} fingerprints"
        )
        
        return fingerprints
    except Exception as e:
        results.add_result(
            "Direct Fingerprint Generation",
            False,
            f"Error: {str(e)}"
        )
        return None


def test_fingerprint_storage(fingerprints):
    """Test 9: Fingerprint Storage"""
    print("\n🧪 Test 9: Fingerprint Storage")
    
    if not fingerprints:
        results.add_result(
            "Fingerprint Storage",
            False,
            "No fingerprints to test with"
        )
        return
    
    try:
        storage = FingerprintStorage()
        test_file = Path("data/fingerprints/test_storage.enc")
        
        storage.save_encrypted(fingerprints, test_file)
        file_exists = test_file.exists()
        
        loaded = storage.load_encrypted(test_file)
        data_matches = (
            loaded['queries'] == fingerprints['queries'] and
            loaded['responses'] == fingerprints['responses']
        )
        
        if test_file.exists():
            test_file.unlink()
        
        results.add_result(
            "Fingerprint Storage",
            file_exists and data_matches,
            "Successfully saved and loaded encrypted fingerprints"
        )
    except Exception as e:
        results.add_result(
            "Fingerprint Storage",
            False,
            f"Error: {str(e)}"
        )


def test_fingerprint_validator():
    """Test 10: Fingerprint Validator"""
    print("\n🧪 Test 10: Fingerprint Validator")
    try:
        validator = FingerprintValidator()
        
        master = validator.get_master_fingerprints()
        
        is_dict = isinstance(master, dict)
        has_keys = 'queries' in master and 'responses' in master
        
        results.add_result(
            "Fingerprint Validator",
            is_dict and has_keys,
            f"Validator loaded {len(master.get('queries', []))} fingerprints"
        )
    except Exception as e:
        results.add_result(
            "Fingerprint Validator",
            False,
            f"Error: {str(e)}"
        )


def test_intent_parsing(agent: ProvenanceGuardian):
    """Test 11: Intent Parsing"""
    print("\n🧪 Test 11: Intent Parsing")
    try:
        test_cases = [
            ("help", "help"),
            ("audit this model", "audit"),
            ("verify yourself", "self_verify"),
            ("how do I fingerprint", "fingerprint_guide"),
            ("random text", "unknown"),
        ]
        
        all_correct = True
        for message, expected in test_cases:
            intent = agent._parse_intent(message)
            if intent != expected:
                all_correct = False
                logger.error(f"Intent parsing failed: '{message}' -> got '{intent}', expected '{expected}'")
        
        results.add_result(
            "Intent Parsing",
            all_correct,
            f"Tested {len(test_cases)} intent patterns"
        )
    except Exception as e:
        results.add_result(
            "Intent Parsing",
            False,
            f"Error: {str(e)}"
        )


def test_model_path_extraction(agent: ProvenanceGuardian):
    """Test 12: Model Path Extraction"""
    print("\n🧪 Test 12: Model Path Extraction")
    try:
        test_cases = [
            ("audit meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-hf"),
            ('audit "my-model"', "my-model"),
            ("audit ./local/model", "./local/model"),
        ]
        
        all_correct = True
        for message, expected in test_cases:
            path = agent._extract_model_path(message)
            if path != expected:
                all_correct = False
                logger.error(f"Path extraction failed: '{message}' -> got '{path}', expected '{expected}'")
        
        results.add_result(
            "Model Path Extraction",
            all_correct,
            f"Tested {len(test_cases)} path patterns"
        )
    except Exception as e:
        results.add_result(
            "Model Path Extraction",
            False,
            f"Error: {str(e)}"
        )


async def main():
    """Run all tests"""
    print("🧪 PROVENANCE GUARDIAN - COMPREHENSIVE BACKEND TESTS")
    print("="*60)
    
    # Initialize agent
    agent = await test_agent_initialization()
    
    if agent:
        # Agent command tests
        await test_help_command(agent)
        await test_self_verification(agent)
        await test_fingerprint_generation(agent)
        await test_fingerprint_guide(agent)
        await test_unknown_command(agent)
        
        # Service tests
        test_fingerprint_service()
        fingerprints = await test_fingerprint_generation_direct()
        test_fingerprint_storage(fingerprints)
        test_fingerprint_validator()
        
        # Utility tests
        test_intent_parsing(agent)
        test_model_path_extraction(agent)
    
    # Print summary
    results.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())