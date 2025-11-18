"""
CPS Automated Greenhouse System using LangGraph Agentic Framework
Demonstrates multi-agent coordination for Cyber-Physical Systems
"""

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain.tools import tool
import random
from datetime import datetime
import json


# ==================== State Definition ====================
class GreenhouseState(TypedDict):
    """Shared state across all agents in the greenhouse system"""
    # Environmental sensors
    temperature: float  # Celsius
    humidity: float  # Percentage (0-100)
    soil_moisture: float  # Percentage (0-100)
    light_level: float  # Lux

    # Actuator states
    heater_on: bool
    fan_on: bool
    water_pump_on: bool
    grow_lights_on: bool

    # Control parameters
    target_temperature: float
    target_humidity: float
    target_soil_moisture: float
    target_light_hours: int

    # Agent messages and decisions
    messages: Annotated[List[str], lambda x, y: x + [y]]
    monitoring_agent_log: List[str]
    control_agent_log: List[str]
    optimization_agent_log: List[str]

    # System status
    timestamp: str
    alert_level: str  # "normal", "warning", "critical"


# ==================== Helpers (diff + formatting) ====================
def _fmt_bool(b: bool) -> str:
    return "ON" if b else "OFF"


def diff_state(prev: GreenhouseState, curr: GreenhouseState) -> str:
    """Return a one-line summary of what changed this cycle and by how much."""
    parts = []
    # Numerical sensors
    for k, unit in [
        ("temperature", "°C"),
        ("humidity", "%"),
        ("soil_moisture", "%"),
        ("light_level", " lux"),
    ]:
        if k in prev and k in curr and prev[k] != curr[k]:
            parts.append(f"{k}: {prev[k]}→{curr[k]}{unit}")
    # Actuators
    for k, label in [
        ("heater_on", "Heater"),
        ("fan_on", "Fan"),
        ("water_pump_on", "Pump"),
        ("grow_lights_on", "Lights"),
    ]:
        if k in prev and k in curr and prev[k] != curr[k]:
            parts.append(f"{label}: {_fmt_bool(prev[k])}→{_fmt_bool(curr[k])}")
    # Targets
    for k, label in [
        ("target_temperature", "TargetTemp"),
        ("target_humidity", "TargetRH"),
        ("target_soil_moisture", "TargetSoil"),
    ]:
        if k in prev and k in curr and prev[k] != curr[k]:
            parts.append(f"{label}: {prev[k]}→{curr[k]}")
    # Alert level
    if prev.get("alert_level") != curr.get("alert_level"):
        parts.append(
            f"Alert: {prev.get('alert_level','?').upper()}→{curr.get('alert_level','?').upper()}"
        )
    return "; ".join(parts) if parts else "No material changes"


# ==================== Physical Simulation Tools ====================
@tool
def read_temperature() -> float:
    """Read current greenhouse temperature in Celsius"""
    # Simulate sensor reading with some variation
    return round(random.uniform(18.0, 32.0), 2)


@tool
def read_humidity() -> float:
    """Read current greenhouse humidity percentage"""
    return round(random.uniform(40.0, 90.0), 2)


@tool
def read_soil_moisture() -> float:
    """Read current soil moisture percentage"""
    return round(random.uniform(30.0, 85.0), 2)


@tool
def read_light_level() -> float:
    """Read current light level in Lux"""
    return round(random.uniform(500.0, 15000.0), 2)


@tool
def set_heater(state: bool) -> str:
    """Turn heater on or off"""
    return f"Heater {'ON' if state else 'OFF'}"


@tool
def set_fan(state: bool) -> str:
    """Turn ventilation fan on or off"""
    return f"Fan {'ON' if state else 'OFF'}"


@tool
def set_water_pump(state: bool) -> str:
    """Turn irrigation water pump on or off"""
    return f"Water pump {'ON' if state else 'OFF'}"


@tool
def set_grow_lights(state: bool) -> str:
    """Turn grow lights on or off"""
    return f"Grow lights {'ON' if state else 'OFF'}"


# ==================== Agent Definitions ====================
class MonitoringAgent:
    """
    Agent 1: Monitoring Agent
    Continuously monitors sensor readings and detects anomalies
    """

    def __init__(self, llm):
        self.llm = llm
        self.tools = [read_temperature, read_humidity, read_soil_moisture, read_light_level]

    def __call__(self, state: GreenhouseState) -> GreenhouseState:
        """Monitor all sensors and log readings"""
        print("\n[Monitoring Agent] Reading sensors...")

        # Read all sensors
        temp = read_temperature.invoke({})
        humidity = read_humidity.invoke({})
        soil = read_soil_moisture.invoke({})
        light = read_light_level.invoke({})

        # Update state with sensor readings
        state["temperature"] = temp
        state["humidity"] = humidity
        state["soil_moisture"] = soil
        state["light_level"] = light
        state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log monitoring data
        log_entry = (
            f"[{state['timestamp']}] "
            f"Temp: {temp}°C, "
            f"Humidity: {humidity}%, "
            f"Soil: {soil}%, "
            f"Light: {light} lux"
        )
        state["monitoring_agent_log"].append(log_entry)
        state["messages"].append(f"Monitoring: {log_entry}")

        print(f"  {log_entry}")

        # Detect critical/warning conditions
        alert = "normal"
        if temp > 30 or temp < 15:
            alert = "critical"
        elif humidity < 35 or humidity > 85:
            alert = "warning"
        elif soil < 20:
            alert = "critical"

        state["alert_level"] = alert
        if alert != "normal":
            state["messages"].append(f"ALERT ({alert.upper()}): Anomaly detected!")

        return state


class ControlAgent:
    """
    Agent 2: Control Agent
    Uses the LLM as a policy to choose actuator states based on sensor readings.
    Falls back to deterministic rules if no LLM or invalid output.
    """

    def __init__(self, llm):
        self.llm = llm
        self.tools = [set_heater, set_fan, set_water_pump, set_grow_lights]

    # ---- deterministic fallback (your old rule-based policy) ----
    def _fallback_policy(self, state: GreenhouseState) -> GreenhouseState:
        print("\n[Control Agent] Fallback deterministic control policy...")

        temp = state["temperature"]
        humidity = state["humidity"]
        soil = state["soil_moisture"]
        light = state["light_level"]
        target_temp = state["target_temperature"]
        target_humid = state["target_humidity"]
        target_soil = state["target_soil_moisture"]

        actions = []
        reasons = []

        # Temperature control
        if temp < target_temp - 2:
            state["heater_on"] = True
            state["fan_on"] = False
            actions.append(set_heater.invoke({"state": True}))
            actions.append(set_fan.invoke({"state": False}))
            reasons.append(f"Heater ON because T={temp} < {target_temp-2} (target-2)")
        elif temp > target_temp + 2:
            state["heater_on"] = False
            state["fan_on"] = True
            actions.append(set_heater.invoke({"state": False}))
            actions.append(set_fan.invoke({"state": True}))
            reasons.append(f"Fan ON, Heater OFF because T={temp} > {target_temp+2} (target+2)")
        else:
            state["heater_on"] = False
            state["fan_on"] = False
            actions.append(set_heater.invoke({"state": False}))
            actions.append(set_fan.invoke({"state": False}))
            reasons.append(f"T in band [{target_temp-2},{target_temp+2}] → Heater OFF, Fan OFF")

        # Humidity
        if humidity > target_humid + 5:
            state["fan_on"] = True
            actions.append(set_fan.invoke({"state": True}))
            reasons.append(f"Fan ON due to RH={humidity} > {target_humid+5} (target+5)")

        # Soil moisture
        if soil < target_soil - 5:
            state["water_pump_on"] = True
            actions.append(set_water_pump.invoke({"state": True}))
            prev_soil = state["soil_moisture"]
            state["soil_moisture"] = min(100, state["soil_moisture"] + 15)
            reasons.append(
                f"Pump ON because soil={soil} < {target_soil-5}; soil {prev_soil}→{state['soil_moisture']}"
            )
        else:
            state["water_pump_on"] = False
            actions.append(set_water_pump.invoke({"state": False}))
            reasons.append(f"Pump OFF because soil={soil} ≥ {target_soil-5}")

        # Light control
        if light < 1000:
            state["grow_lights_on"] = True
            actions.append(set_grow_lights.invoke({"state": True}))
            reasons.append(f"Lights ON because light={light} < 1000 lux")
        else:
            state["grow_lights_on"] = False
            actions.append(set_grow_lights.invoke({"state": False}))
            reasons.append(f"Lights OFF because light={light} ≥ 1000 lux")

        log_entry = f"[{state['timestamp']}] Control actions (fallback): {', '.join(actions)}"
        why_entry = (
            f"[{state['timestamp']}] Reasons (fallback):\n"
            + "\n".join(f"  • {r}" for r in reasons)
        )

        state["control_agent_log"].append(log_entry)
        state["control_agent_log"].append(why_entry)
        state["messages"].append(f"Control: {log_entry}")
        state["messages"].append(f"ControlWhy: {why_entry}")

        print(f"  {log_entry}")
        print(f"  {why_entry}")

        return state

    # ---- main LLM policy ----
    def __call__(self, state: GreenhouseState) -> GreenhouseState:
        # If no LLM, just use the deterministic policy
        if self.llm is None:
            return self._fallback_policy(state)

        print("\n[Control Agent] Evaluating control actions via LLM policy...")

        recent_monitor = state["monitoring_agent_log"][-3:]
        recent_control = state["control_agent_log"][-3:]
        recent_history = "\n".join(recent_monitor + recent_control) or "No prior history (first cycle)."

        temp = state["temperature"]
        humidity = state["humidity"]
        soil = state["soil_moisture"]
        light = state["light_level"]

        target_temp = state["target_temperature"]
        target_humid = state["target_humidity"]
        target_soil = state["target_soil_moisture"]
        target_light_hours = state["target_light_hours"]

        # build a strict JSON-output prompt
        prompt = f"""
You are an autonomous control agent for an automated greenhouse cyber-physical system.

YOUR OBJECTIVES (in order of priority):
1. Keep plants within safe environmental ranges (avoid stressing or killing them).
2. Stay reasonably close to the target setpoints over time (good growing conditions).
3. Minimize energy use (heater, fan, grow lights) and water use (pump).
4. Avoid rapid oscillation (toggling actuators on/off every cycle without need).

You are given:
- Current sensor readings:
  - temperature_c: {temp}
  - humidity_percent: {humidity}
  - soil_moisture_percent: {soil}
  - light_level_lux: {light}

- Current control targets:
  - target_temperature_c: {target_temp}
  - target_humidity_percent: {target_humid}
  - target_soil_moisture_percent: {target_soil}
  - target_light_hours: {target_light_hours}

- Previous alert_level: {state.get("alert_level", "normal")}

- Recent history (monitoring + control logs, most recent last):
{recent_history}

INTERPRETATION GUIDELINES (YOU choose exact thresholds):
- "normal": all readings are safe for plants and roughly near targets.
- "warning": readings are drifting away from targets or trending in a bad direction,
             but not yet immediately dangerous.
- "critical": readings are unsafe for plants OR require urgent strong action.

You are free to:
- Keep actuators OFF if conditions are already good and stable.
- Turn actuators ON preemptively if readings are moving toward unsafe ranges.
- Leave actuators as they are to avoid unnecessary toggling.
- Escalate alert_level if you believe the situation is warning or critical,
  based on both current readings and recent history.

You MUST respond with ONLY a valid JSON object with these keys:
  "heater_on": true or false,
  "fan_on": true or false,
  "water_pump_on": true or false,
  "grow_lights_on": true or false,
  "alert_level": one of "normal", "warning", "critical",
  "reason": a short human-readable explanation string.

The "reason" should briefly explain:
- why you chose these actuator settings,
- what trade-offs you made (plant safety vs. energy/water vs. stability),
- and any trend you noticed from the recent history (if relevant).

Return JSON only. No backticks, no code fences, no extra commentary.
"""
        try:
            llm_result = self.llm.invoke(prompt)
            raw = getattr(llm_result, "content", str(llm_result)).strip()
              # --- NEW: strip ```json fences if present ---
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("LLM output did not contain a JSON object")

            json_str = raw[start : end + 1]

            decision = json.loads(json_str)
        except Exception as e:
            print(f"  [LLM Control ERROR] {e}")
            print(f"  [LLM Raw Response] {locals().get('raw', 'N/A')}")
            return self._fallback_policy(state)

        # Extract booleans with safe defaulting
        heater_on = bool(decision.get("heater_on", state.get("heater_on", False)))
        fan_on = bool(decision.get("fan_on", state.get("fan_on", False)))
        pump_on = bool(decision.get("water_pump_on", state.get("water_pump_on", False)))
        lights_on = bool(decision.get("grow_lights_on", state.get("grow_lights_on", False)))
        alert_level = decision.get("alert_level", state.get("alert_level", "normal"))
        reason = decision.get("reason", "LLM policy decision")

        # Update state
        state["heater_on"] = heater_on
        state["fan_on"] = fan_on
        state["water_pump_on"] = pump_on
        state["grow_lights_on"] = lights_on
        state["alert_level"] = alert_level

        # Simulate physical effect of watering (optional, same as before)
        if pump_on:
            prev_soil = state["soil_moisture"]
            state["soil_moisture"] = min(100, state["soil_moisture"] + 15)
        else:
            prev_soil = state["soil_moisture"]

        # Call tools (this is your “actuator interface”)
        actions = []
        actions.append(set_heater.invoke({"state": heater_on}))
        actions.append(set_fan.invoke({"state": fan_on}))
        actions.append(set_water_pump.invoke({"state": pump_on}))
        actions.append(set_grow_lights.invoke({"state": lights_on}))

        log_entry = f"[{state['timestamp']}] Control actions (LLM): {', '.join(actions)}"
        why_entry = (
            f"[{state['timestamp']}] LLM Reason: {reason} "
            f"(alert_level={alert_level}, soil_before={prev_soil}, soil_after={state['soil_moisture']})"
        )

        state["control_agent_log"].append(log_entry)
        state["control_agent_log"].append(why_entry)
        state["messages"].append(f"Control: {log_entry}")
        state["messages"].append(f"ControlWhy: {why_entry}")

        print(f"  {log_entry}")
        print(f"  {why_entry}")

        return state

class OptimizationAgent:
    """
    Agent 3: Optimization Agent
    Analyzes historical data and optimizes target parameters
    """

    def __init__(self, llm):
        self.llm = llm

    def _fallback_optimize(self, state: GreenhouseState) -> GreenhouseState:
        """Old deterministic optimization policy (safety fallback)"""
        print("\n[Optimization Agent] Deterministic optimization...")
        temp = state["temperature"]
        recent_actions = len([m for m in state["control_agent_log"][-5:] if "ON" in m])

        if recent_actions > 3:
            if abs(temp - state["target_temperature"]) < 1:
                state["target_temperature"] = round(state["target_temperature"] + 0.5, 1)
                optimization = "Adjusted target temp for efficiency"
                why = f"recent_actions={recent_actions} (>3) and |T-Target|<1"
            else:
                optimization = "System operating efficiently"
                why = f"recent_actions={recent_actions} but |T-Target|≥1"
        else:
            optimization = "System stable, no optimization needed"
            why = f"recent_actions={recent_actions} (≤3)"

        log_entry = f"[{state['timestamp']}] {optimization} ({why})"
        state["optimization_agent_log"].append(log_entry)
        state["messages"].append(f"Optimization: {log_entry}")

        print(f"  {log_entry}")
        return state

    def __call__(self, state: GreenhouseState) -> GreenhouseState:
        """Optimize target parameters based on plant health, comfort & efficiency"""
        print("\n[Optimization Agent] Analyzing performance...")

        # If no LLM configured, fall back to deterministic
        if self.llm is None:
            return self._fallback_optimize(state)

        # Collect context for the LLM
        current_targets = {
            "target_temperature": state["target_temperature"],
            "target_humidity": state["target_humidity"],
            "target_soil_moisture": state["target_soil_moisture"],
            "target_light_hours": state["target_light_hours"],
        }

        recent_monitor = "\n".join(state["monitoring_agent_log"][-10:]) or "No monitoring logs."
        recent_control = "\n".join(state["control_agent_log"][-10:]) or "No control logs."

        prompt = f"""
You are the optimization agent for an automated greenhouse CPS.

Your job is to periodically adjust the control setpoints to balance:
- plant health and comfort,
- energy efficiency (heater, fan, lights),
- water efficiency (pump),
- and actuator wear (avoid excessive ON/OFF cycling).

You are given:
- Current targets:
  - target_temperature_c: {current_targets['target_temperature']}
  - target_humidity_percent: {current_targets['target_humidity']}
  - target_soil_moisture_percent: {current_targets['target_soil_moisture']}
  - target_light_hours: {current_targets['target_light_hours']}

- Recent monitoring logs (oldest to newest):
{recent_monitor}

- Recent control logs (oldest to newest):
{recent_control}

General guidelines (but you may deviate with justification):
- Comfortable greenhouse temps are typically in roughly the 18–28°C range.
- Humidity around 50–70% is often acceptable for many plants.
- Soil moisture should not stay at extremes (0–10% or 90–100%) for long.
- More actuator ON time => higher energy/water usage; consider relaxing targets slightly.

Respond ONLY with JSON:
{{
  "target_temperature": <float, new target temp in °C>,
  "target_humidity": <float, new target humidity in %>,
  "target_soil_moisture": <float, new target soil moisture in %>,
  "target_light_hours": <int, new target daily light hours>,
  "reason": "<short explanation of trade-offs and why you changed or kept each target>"
}}
"""

        try:
            llm_result = self.llm.invoke(prompt)
            raw = getattr(llm_result, "content", str(llm_result)).strip()

            # slice JSON
            s = raw.find("{")
            e = raw.rfind("}")
            if s == -1 or e == -1:
                raise ValueError("LLM output did not contain a JSON object")
            json_str = raw[s : e + 1]

            decision = json.loads(json_str)
        except Exception as e:
            print(f"  [Optimization LLM ERROR] {e}")
            print(f"  [Optimization LLM Raw] {locals().get('raw', 'N/A')}")
            return self._fallback_optimize(state)

        # Safely apply new targets with clamping
        def clamp(val, lo, hi, default):
            try:
                v = float(val)
            except Exception:
                return default
            return max(lo, min(hi, v))

        new_temp = clamp(decision.get("target_temperature", current_targets["target_temperature"]),
                         10.0, 35.0, current_targets["target_temperature"])
        new_humid = clamp(decision.get("target_humidity", current_targets["target_humidity"]),
                          20.0, 90.0, current_targets["target_humidity"])
        new_soil = clamp(decision.get("target_soil_moisture", current_targets["target_soil_moisture"]),
                         10.0, 90.0, current_targets["target_soil_moisture"])
        try:
            new_light_hours = int(decision.get("target_light_hours", current_targets["target_light_hours"]))
            new_light_hours = max(4, min(20, new_light_hours))
        except Exception:
            new_light_hours = current_targets["target_light_hours"]

        reason = decision.get("reason", "LLM optimization decision")

        # Apply to state
        state["target_temperature"] = round(new_temp, 1)
        state["target_humidity"] = round(new_humid, 1)
        state["target_soil_moisture"] = round(new_soil, 1)
        state["target_light_hours"] = new_light_hours

        log_entry = (
            f"[{state['timestamp']}] LLM optimization: "
            f"T={state['target_temperature']}°C, "
            f"RH={state['target_humidity']}%, "
            f"Soil={state['target_soil_moisture']}%, "
            f"LightHours={state['target_light_hours']}"
        )
        why_entry = f"[{state['timestamp']}] LLM optimization reason: {reason}"

        state["optimization_agent_log"].append(log_entry)
        state["optimization_agent_log"].append(why_entry)
        state["messages"].append(f"Optimization: {log_entry}")
        state["messages"].append(f"OptimizationWhy: {why_entry}")

        print(f"  {log_entry}")
        print(f"  {why_entry}")

        return state

# ==================== LangGraph Workflow Definition ====================
def create_greenhouse_workflow():
    """
    Create the LangGraph state machine for the greenhouse system

    This demonstrates the Agentic AI stack:
    1. Planning Layer: Workflow graph structure
    2. Execution Layer: Agent nodes with tools
    3. Memory Layer: Shared state persistence
    4. Feedback Layer: Continuous monitoring and adaptation
    """

    # LLM can be used for advanced decision-making, but not required for this demo
    # The agents use deterministic logic, but LLM can enhance decision-making
    try:
        llm = ChatOllama(model="llama3.1", temperature=0)
    except Exception:
        llm = None  # Will work with deterministic agents

    # Initialize agents
    monitoring_agent = MonitoringAgent(llm)
    control_agent = ControlAgent(llm)
    optimization_agent = OptimizationAgent(llm)

    # Create state graph with state schema
    workflow = StateGraph(GreenhouseState)

    # Add nodes (agents)
    workflow.add_node("monitor", monitoring_agent)
    workflow.add_node("control", control_agent)
    workflow.add_node("optimize", optimization_agent)

    # Define workflow edges
    workflow.set_entry_point("monitor")
    workflow.add_edge("monitor", "control")
    workflow.add_edge("control", "optimize")

    # Conditional routing based on alert level
    def route_by_alert(state: GreenhouseState):
        if state.get("alert_level") == "critical":
            return "monitor"  # Re-monitor immediately
        else:
            return END

    workflow.add_conditional_edges(
        "optimize",
        route_by_alert,
        {
            "monitor": "monitor",
            END: END,
        },
    )

    return workflow.compile()


# ==================== Main Execution ====================
def initialize_state() -> GreenhouseState:
    """Initialize the greenhouse system state"""
    return GreenhouseState(
        temperature=22.0,
        humidity=60.0,
        soil_moisture=50.0,
        light_level=5000.0,
        heater_on=False,
        fan_on=False,
        water_pump_on=False,
        grow_lights_on=False,
        target_temperature=24.0,
        target_humidity=65.0,
        target_soil_moisture=60.0,
        target_light_hours=12,
        messages=[],
        monitoring_agent_log=[],
        control_agent_log=[],
        optimization_agent_log=[],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        alert_level="normal",
    )


def run_demo():
    """Run the CPS greenhouse system demonstration"""
    print("=" * 70)
    print("CPS AUTOMATED GREENHOUSE SYSTEM - LangGraph Agentic Framework Demo")
    print("=" * 70)

    # Create workflow
    app = create_greenhouse_workflow()

    # Initialize state
    current_state = initialize_state()

    print("\nInitial State:")
    print(f"  Target Temperature: {current_state['target_temperature']}°C")
    print(f"  Target Humidity: {current_state['target_humidity']}%")
    print(f"  Target Soil Moisture: {current_state['target_soil_moisture']}%")

    # Run simulation cycles
    print("\n" + "=" * 70)
    print("SIMULATION CYCLES")
    print("=" * 70)

    for cycle in range(5):
        print(f"\n{'=' * 70}")
        print(f"CYCLE {cycle + 1}")
        print(f"{'=' * 70}")

        # Snapshot for delta
        prev_state = current_state.copy()  # shallow copy is fine for these fields

        # Execute workflow
        result = app.invoke(current_state)
        current_state = result

        # Delta summary
        delta = diff_state(prev_state, current_state)
        print(f"\n[Delta This Cycle] {delta}")

        # Show last control 'why' line for this cycle (if any)
        last_whys = [m for m in current_state["control_agent_log"] if "Reasons:" in m]
        if last_whys:
            print(f"[Control Why] {last_whys[-1]}")

        # Display final state
        print(f"\n[System State After Cycle {cycle + 1}]")
        print(f"  Temperature: {current_state['temperature']}°C")
        print(f"  Humidity: {current_state['humidity']}%")
        print(f"  Soil Moisture: {current_state['soil_moisture']}%")
        print(f"  Light Level: {current_state['light_level']} lux")
        print(f"  Alert Level: {current_state['alert_level'].upper()}")
        print(
            f"  Actuators: Heater={current_state['heater_on']}, "
            f"Fan={current_state['fan_on']}, "
            f"Pump={current_state['water_pump_on']}, "
            f"Lights={current_state['grow_lights_on']}"
        )

        if cycle < 4:  # Don't wait after last cycle
            print("\nWaiting 2 seconds before next cycle...")
            import time
            time.sleep(2)

    # Display summary
    print("\n" + "=" * 70)
    print("SYSTEM SUMMARY")
    print("=" * 70)
    print(f"\nTotal Monitoring Entries: {len(current_state['monitoring_agent_log'])}")
    print(f"Total Control Actions: {len(current_state['control_agent_log'])}")
    print(f"Total Optimizations: {len(current_state['optimization_agent_log'])}")

    print("\n" + "=" * 70)
    print("AGENTIC AI STACK ANALYSIS")
    print("=" * 70)
    print_agentic_stack_analysis()


def print_agentic_stack_analysis():
    """
    Relate the greenhouse system to the Agentic AI stack
    """
    analysis = """
    ┌─────────────────────────────────────────────────────────────┐
    │ AGENTIC AI STACK IN CPS GREENHOUSE SYSTEM                   │
    └─────────────────────────────────────────────────────────────┘

    1. PLANNING LAYER
       └─ LangGraph StateGraph defines the workflow structure
          • Nodes: monitor → control → optimize
          • Conditional routing based on alert levels
          • Enables dynamic decision-making

    2. EXECUTION LAYER
       └─ Three specialized agents with tools:
          • Monitoring Agent: Sensor reading tools (temperature, humidity, etc.)
          • Control Agent: Actuator control tools (heater, fan, pump, lights)
          • Optimization Agent: Analysis and parameter tuning
          • Each agent operates autonomously but coordinates through shared state

    3. MEMORY LAYER
       └─ GreenhouseState (TypedDict) maintains:
          • Sensor readings (current state)
          • Actuator states (control outputs)
          • Agent logs (historical decisions)
          • System parameters (targets and configurations)
          • Messages (inter-agent communication)

    4. FEEDBACK LAYER
       └─ Continuous adaptation through:
          • Real-time sensor monitoring → state updates
          • Control decisions → actuator actions → environmental changes
          • Optimization analysis → parameter adjustments
          • Alert detection → workflow rerouting

    5. TOOL LAYER (LangChain Tools)
       └─ Physical world interface:
          • read_temperature, read_humidity, read_soil_moisture, read_light_level
          • set_heater, set_fan, set_water_pump, set_grow_lights
          • Tools bridge the digital agents with physical CPS components

    KEY AGENTIC PRINCIPLES DEMONSTRATED:
    ✓ Multi-agent coordination
    ✓ Shared state management
    ✓ Tool use for CPS actuation
    ✓ Autonomous decision-making
    ✓ Reactive workflow adaptation
    ✓ Continuous monitoring and optimization
    """
    print(analysis)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError running demo: {e}")
        import traceback
        traceback.print_exc()
        print("\nTrying test script instead: python test_system.py")