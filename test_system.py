"""
Simple test script to verify the greenhouse system works
"""

import sys

def test_imports():
    """Test that all required packages can be imported"""
    try:
        from typing import TypedDict, Annotated, List
        print("✓ Typing imports OK")
        
        try:
            from langgraph.graph import StateGraph, END
            print("✓ LangGraph imports OK")
        except ImportError as e:
            print(f"⚠ LangGraph not installed: {e}")
            print("  Install with: pip install langgraph")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_state_definition():
    """Test that the state can be created"""
    try:
        from greenhouse_cps import GreenhouseState, initialize_state
        
        state = initialize_state()
        assert "temperature" in state
        assert "humidity" in state
        assert "target_temperature" in state
        print("✓ State definition OK")
        return True
    except Exception as e:
        print(f"✗ State definition error: {e}")
        return False

def test_tools():
    """Test that tools can be invoked"""
    try:
        from greenhouse_cps import read_temperature, read_humidity, set_heater
        
        temp = read_temperature.invoke({})
        assert isinstance(temp, (int, float))
        print(f"✓ Tools work: read_temperature() = {temp}")
        
        result = set_heater.invoke(True)
        assert "ON" in result or "OFF" in result
        print(f"✓ Tools work: {result}")
        
        return True
    except Exception as e:
        print(f"✗ Tools error: {e}")
        return False

def test_agents():
    """Test that agents can be instantiated"""
    try:
        from greenhouse_cps import MonitoringAgent, ControlAgent, OptimizationAgent
        
        # Agents can work without LLM for this demo
        monitor = MonitoringAgent(None)
        control = ControlAgent(None)
        optimize = OptimizationAgent(None)
        
        print("✓ Agents can be instantiated")
        return True
    except Exception as e:
        print(f"✗ Agent instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow():
    """Test that workflow can be created (without running it)"""
    try:
        from greenhouse_cps import create_greenhouse_workflow
        app = create_greenhouse_workflow()
        print("✓ Workflow can be created")
        return True
    except Exception as e:
        print(f"✗ Workflow creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing CPS Greenhouse System...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("State Definition", test_state_definition),
        ("Tools", test_tools),
        ("Agents", test_agents),
        ("Workflow", test_workflow),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! You can run: python greenhouse_cps.py")
    else:
        print("\n⚠ Some tests failed. Check the errors above.")
        sys.exit(1)
