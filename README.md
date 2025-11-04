# CPS Automated Greenhouse System Using LangGraph

## Why LangGraph

- **State Management:** Built-in state persistence across agent interactions enables seamless coordination between monitoring, control, and optimization agents without manual state handling.

- **Workflow Orchestration:** Declarative graph definition makes complex multi-agent workflows easy to understand, modify, and extend. Sequential and conditional edges provide fine-grained control flow.

- **Reactive Adaptation:** Conditional routing based on system state (alert levels) enables the workflow to adapt dynamically—critical alerts trigger immediate re-monitoring without waiting for the next cycle.

- **Extensible:** Swap simulated tools for real hardware interfaces (GPIO, I2C, SCADA) without changing the graph structure. Add new agents (e.g., predictive maintenance) by simply adding nodes.

- **Production-Ready:** Designed for building robust, scalable agentic systems with proper error handling, state checkpoints, and audit trails.

## How it Works/What's Included

- **State definition** (`GreenhouseState` TypedDict) - Shared state containing sensor readings, actuator states, target parameters, and agent logs

- **Sensor Tools** (`read_temperature`, `read_humidity`, `read_soil_moisture`, `read_light_level`) - Interface for reading physical sensors

- **Actuator Tools** (`set_heater`, `set_fan`, `set_water_pump`, `set_grow_lights`) - Interface for controlling physical devices

- **Nodes:** 
  - **Monitoring Agent** - Reads sensors, detects anomalies, sets alert levels
  - **Control Agent** - Makes real-time decisions, controls actuators based on sensor readings vs. targets
  - **Optimization Agent** - Analyzes performance, adjusts target parameters for efficiency

- **Graph wiring** - Sequential edges (monitor → control → optimize) with conditional routing (critical alerts loop back to monitor)

- **Demo Run:** Executes 5 simulation cycles showing autonomous operation, state flow, and reactive adaptation

## Setup & Run

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install langgraph langchain langchain-openai langchain-community python-dotenv pydantic matplotlib numpy
```

### 3. Configure API Key (Optional)

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

**Note:** The system works without an API key using deterministic agent logic. The API key is optional for enhanced LLM-based decision-making.

### 4. Run the Demo

```bash
python greenhouse_cps.py
```

## Output

### Typical Run

```bash
======================================================================
CPS AUTOMATED GREENHOUSE SYSTEM - LangGraph Agentic Framework Demo
======================================================================

Initial State:
  Target Temperature: 24.0°C
  Target Humidity: 65.0%
  Target Soil Moisture: 60.0%

======================================================================
SIMULATION CYCLES
======================================================================

======================================================================
CYCLE 1
======================================================================

[Monitoring Agent] Reading sensors...
  [2025-11-04 14:37:56] Temp: 21.01°C, Humidity: 47.67%, Soil: 72.42%, Light: 800.76 lux

[Control Agent] Evaluating control actions...
  [2025-11-04 14:37:56] Control actions: Heater ON, Water pump OFF, Grow lights ON

[Optimization Agent] Analyzing performance...
  [2025-11-04 14:37:56] System stable, no optimization needed

[System State After Cycle 1]
  Temperature: 21.01°C
  Humidity: 47.67%
  Soil Moisture: 72.42%
  Light Level: 800.76 lux
  Alert Level: NORMAL
  Actuators: Heater=True, Fan=False, Pump=False, Lights=True

======================================================================
CYCLE 2
======================================================================

[Monitoring Agent] Reading sensors...
  [2025-11-04 14:37:58] Temp: 21.17°C, Humidity: 53.05%, Soil: 79.25%, Light: 8831.22 lux

[Control Agent] Evaluating control actions...
  [2025-11-04 14:37:58] Control actions: Heater ON, Water pump OFF, Grow lights OFF

[Optimization Agent] Analyzing performance...
  [2025-11-04 14:37:58] System stable, no optimization needed

[System State After Cycle 2]
  Temperature: 21.17°C
  Humidity: 53.05%
  Soil Moisture: 79.25%
  Light Level: 8831.22 lux
  Alert Level: NORMAL
  Actuators: Heater=True, Fan=False, Pump=False, Lights=False

======================================================================
CYCLE 3
======================================================================

[Monitoring Agent] Reading sensors...
  [2025-11-04 14:38:00] Temp: 20.72°C, Humidity: 69.22%, Soil: 45.5%, Light: 8005.06 lux

[Control Agent] Evaluating control actions...
  [2025-11-04 14:38:00] Control actions: Heater ON, Water pump ON, Grow lights OFF

[Optimization Agent] Analyzing performance...
  [2025-11-04 14:38:00] System stable, no optimization needed

[System State After Cycle 3]
  Temperature: 20.72°C
  Humidity: 69.22%
  Soil Moisture: 60.5%
  Light Level: 8005.06 lux
  Alert Level: NORMAL
  Actuators: Heater=True, Fan=False, Pump=True, Lights=False

======================================================================
CYCLE 4
======================================================================

[Monitoring Agent] Reading sensors...
  [2025-11-04 14:38:02] Temp: 24.64°C, Humidity: 76.85%, Soil: 77.14%, Light: 12548.29 lux

[Control Agent] Evaluating control actions...
  [2025-11-04 14:38:02] Control actions: Heater OFF, Fan OFF, Fan ON, Water pump OFF, Grow lights OFF

[Optimization Agent] Analyzing performance...
  [2025-11-04 14:38:02] Adjusted target temp for efficiency

[System State After Cycle 4]
  Temperature: 24.64°C
  Humidity: 76.85%
  Soil Moisture: 77.14%
  Light Level: 12548.29 lux
  Alert Level: NORMAL
  Actuators: Heater=False, Fan=True, Pump=False, Lights=False

======================================================================
CYCLE 5
======================================================================

[Monitoring Agent] Reading sensors...
  [2025-11-04 14:38:04] Temp: 31.5°C, Humidity: 43.41%, Soil: 63.95%, Light: 11461.36 lux

[Control Agent] Evaluating control actions...
  [2025-11-04 14:38:04] Control actions: Heater OFF, Fan ON, Water pump OFF, Grow lights OFF

[Optimization Agent] Analyzing performance...
  [2025-11-04 14:38:04] System operating efficiently

[System State After Cycle 5]
  Temperature: 18.91°C
  Humidity: 70.26%
  Soil Moisture: 67.57%
  Light Level: 2795.77 lux
  Alert Level: NORMAL
  Actuators: Heater=True, Fan=True, Pump=True, Lights=False

======================================================================
SYSTEM SUMMARY
======================================================================

Total Monitoring Entries: 6
Total Control Actions: 6
Total Optimizations: 6

======================================================================
AGENTIC AI STACK ANALYSIS
======================================================================

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
```

### Critical Alert Scenario

When critical conditions are detected, the workflow adapts:

```bash
[Monitoring Agent] Reading sensors...
  [2025-11-04 14:38:04] Temp: 31.5°C, Humidity: 43.41%, Soil: 63.95%, Light: 11461.36 lux
  ALERT (CRITICAL): Anomaly detected!

[Control Agent] Evaluating control actions...
  [2025-11-04 14:38:04] Control actions: Heater OFF, Fan ON, Water pump OFF, Grow lights OFF

[Optimization Agent] Analyzing performance...
  [2025-11-04 14:38:04] System operating efficiently

[Monitoring Agent] Reading sensors...  ← Immediate re-monitoring due to critical alert
  [2025-11-04 14:38:04] Temp: 18.91°C, Humidity: 70.26%, Soil: 52.57%, Light: 2795.77 lux
```

### Mermaid Diagram

The system architecture can be visualized using the diagrams in `architecture_diagram.md`. Here's the core workflow:

```mermaid
graph TB
    Start([System Start]) --> Monitor[Monitoring Agent]
    
    Monitor --> |Updates State| ReadSensors[Read Sensors]
    ReadSensors --> |State Updated| Control[Control Agent]
    
    Control --> |Evaluates Conditions| CheckTemp{Temperature<br/>Check}
    Control --> |Evaluates Conditions| CheckHumidity{Humidity<br/>Check}
    Control --> |Evaluates Conditions| CheckSoil{Soil<br/>Moisture Check}
    Control --> |Evaluates Conditions| CheckLight{Light<br/>Level Check}
    
    CheckTemp -->|Too Low| HeaterON[Heater: ON]
    CheckTemp -->|Too High| FanON[Fan: ON]
    CheckHumidity -->|Too High| FanON2[Fan: ON]
    CheckSoil -->|Too Low| PumpON[Water Pump: ON]
    CheckLight -->|Too Low| LightsON[Grow Lights: ON]
    
    HeaterON --> |State Updated| Optimize[Optimization Agent]
    FanON --> |State Updated| Optimize
    PumpON --> |State Updated| Optimize
    LightsON --> |State Updated| Optimize
    
    Optimize --> |Analyzes Performance| CheckAlert{Alert<br/>Level?}
    
    CheckAlert -->|Critical| Monitor
    CheckAlert -->|Normal/Warning| End([Cycle Complete])
    
    style Monitor fill:#2196F3,color:#ffffff
    style Control fill:#FF9800,color:#ffffff
    style Optimize fill:#4CAF50,color:#ffffff
    style Start fill:#9C27B0,color:#ffffff
    style End fill:#9C27B0,color:#ffffff
```
