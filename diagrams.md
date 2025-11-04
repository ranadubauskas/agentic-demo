# CPS Greenhouse System Architecture Diagrams

## System Workflow Architecture

```mermaid
graph TB
    Start([System Start]) --> Monitor[Monitoring Agent]
    
    Monitor --> |Updates State| ReadSensors[Read Sensors]
    ReadSensors --> TempSensor[Temperature Sensor]
    ReadSensors --> HumiditySensor[Humidity Sensor]
    ReadSensors --> SoilSensor[Soil Moisture Sensor]
    ReadSensors --> LightSensor[Light Level Sensor]
    
    ReadSensors --> |State Updated| Control[Control Agent]
    
    Control --> |Evaluates| CheckTemp{Temperature<br/>Check}
    Control --> |Evaluates| CheckHumidity{Humidity<br/>Check}
    Control --> |Evaluates| CheckSoil{Soil<br/>Moisture Check}
    Control --> |Evaluates| CheckLight{Light<br/>Level Check}
    
    CheckTemp -->|Too Low| HeaterON[Heater: ON]
    CheckTemp -->|Too High| FanON[Fan: ON]
    CheckTemp -->|Optimal| NoHeater[Heater: OFF]
    
    CheckHumidity -->|Too High| FanON2[Fan: ON]
    
    CheckSoil -->|Too Low| PumpON[Water Pump: ON]
    CheckSoil -->|Optimal| PumpOFF[Water Pump: OFF]
    
    CheckLight -->|Too Low| LightsON[Grow Lights: ON]
    CheckLight -->|Optimal| LightsOFF[Grow Lights: OFF]
    
    HeaterON --> |State Updated| Optimize[Optimization Agent]
    FanON --> |State Updated| Optimize
    NoHeater --> |State Updated| Optimize
    FanON2 --> |State Updated| Optimize
    PumpON --> |State Updated| Optimize
    PumpOFF --> |State Updated| Optimize
    LightsON --> |State Updated| Optimize
    LightsOFF --> |State Updated| Optimize
    
    Optimize --> |Analyzes Performance| CheckAlert{Alert<br/>Level?}
    
    CheckAlert -->|Critical| Monitor
    CheckAlert -->|Normal/Warning| End([Cycle Complete])
    
    style Monitor fill:#2196F3,color:#ffffff
    style Control fill:#FF9800,color:#ffffff
    style Optimize fill:#4CAF50,color:#ffffff
    style Start fill:#9C27B0,color:#ffffff
    style End fill:#9C27B0,color:#ffffff
```

## Agent Architecture with Tools

```mermaid
graph LR
    subgraph "Planning Layer: LangGraph Workflow"
        Workflow[StateGraph<br/>Workflow Orchestrator]
    end
    
    subgraph "Execution Layer: Autonomous Agents"
        Monitor[Monitoring Agent<br/>🌡️ Sensor Monitoring]
        Control[Control Agent<br/>⚙️ Actuator Control]
        Optimize[Optimization Agent<br/>📊 Performance Analysis]
    end
    
    subgraph "Memory Layer: Shared State"
        State[(GreenhouseState<br/>• Temperature<br/>• Humidity<br/>• Soil Moisture<br/>• Light Level<br/>• Actuator States<br/>• Target Parameters<br/>• Agent Logs<br/>• Alert Level)]
    end
    
    subgraph "Tool Layer: CPS Interface"
        subgraph "Sensor Tools"
            TTool[read_temperature]
            HTool[read_humidity]
            STool[read_soil_moisture]
            LTool[read_light_level]
        end
        
        subgraph "Actuator Tools"
            HeaterTool[set_heater]
            FanTool[set_fan]
            PumpTool[set_water_pump]
            LightTool[set_grow_lights]
        end
    end
    
    Workflow --> Monitor
    Workflow --> Control
    Workflow --> Optimize
    
    Monitor --> TTool
    Monitor --> HTool
    Monitor --> STool
    Monitor --> LTool
    
    Control --> HeaterTool
    Control --> FanTool
    Control --> PumpTool
    Control --> LightTool
    
    Monitor <--> State
    Control <--> State
    Optimize <--> State
    
    TTool -.->|Physical World| Sensors[Physical Sensors<br/>🌡️💧💡]
    HeaterTool -.->|Physical World| Actuators[Physical Actuators<br/>🔥🌀💧💡]
    
    style Monitor fill:#2196F3,color:#ffffff
    style Control fill:#FF9800,color:#ffffff
    style Optimize fill:#4CAF50,color:#ffffff
    style State fill:#E91E63,color:#ffffff
    style Workflow fill:#673AB7,color:#ffffff
```

## Agentic AI Stack Layers

```mermaid
graph TB
    subgraph "1. Planning Layer"
        Plan[LangGraph StateGraph<br/>• Workflow Definition<br/>• Node Structure<br/>• Conditional Routing<br/>• Dynamic Adaptation]
    end
    
    subgraph "2. Execution Layer"
        Exec1[Monitoring Agent<br/>Autonomous Sensor Reading]
        Exec2[Control Agent<br/>Autonomous Decision Making]
        Exec3[Optimization Agent<br/>Autonomous Analysis]
    end
    
    subgraph "3. Memory Layer"
        Memory[(GreenhouseState TypedDict<br/>• Current Sensor Values<br/>• Actuator States<br/>• Historical Logs<br/>• Target Parameters<br/>• System Status)]
    end
    
    subgraph "4. Feedback Layer"
        Feedback[Adaptation Mechanisms<br/>• Sensor → Control Feedback<br/>• Performance → Optimization<br/>• Alert → Workflow Routing]
    end
    
    subgraph "5. Tool Layer"
        Tools[CPS Interface Tools<br/>• Sensor Reading Tools<br/>• Actuator Control Tools<br/>• Hardware Abstraction]
    end
    
    Plan --> Exec1
    Plan --> Exec2
    Plan --> Exec3
    
    Exec1 --> Memory
    Exec2 --> Memory
    Exec3 --> Memory
    
    Memory --> Feedback
    Feedback --> Plan
    
    Exec1 --> Tools
    Exec2 --> Tools
    
    style Plan fill:#673AB7,color:#ffffff
    style Exec1 fill:#2196F3,color:#ffffff
    style Exec2 fill:#FF9800,color:#ffffff
    style Exec3 fill:#4CAF50,color:#ffffff
    style Memory fill:#E91E63,color:#ffffff
    style Feedback fill:#FFC107,color:#000000
    style Tools fill:#F44336,color:#ffffff
```

## State Flow Diagram

```mermaid
sequenceDiagram
    participant Start as System Start
    participant Monitor as Monitoring Agent
    participant State as GreenhouseState
    participant Control as Control Agent
    participant Optimize as Optimization Agent
    participant Tools as Tools Layer
    participant HW as Physical Hardware
    
    Start->>State: Initialize State
    State->>Monitor: Trigger Monitoring
    
    Monitor->>Tools: read_temperature()
    Tools->>HW: Query Sensor
    HW-->>Tools: Temperature Value
    Tools-->>Monitor: 21.5°C
    
    Monitor->>Tools: read_humidity()
    Tools->>HW: Query Sensor
    HW-->>Tools: Humidity Value
    Tools-->>Monitor: 65%
    
    Monitor->>Tools: read_soil_moisture()
    Monitor->>Tools: read_light_level()
    
    Monitor->>State: Update Sensor Values
    Monitor->>State: Set Alert Level
    Monitor->>State: Log Monitoring Entry
    
    State->>Control: Trigger Control
    
    Control->>State: Read Current Values
    Control->>State: Read Target Parameters
    
    alt Temperature Too Low
        Control->>Tools: set_heater(ON)
        Tools->>HW: Activate Heater
        Control->>State: Update heater_on = True
    else Temperature Too High
        Control->>Tools: set_fan(ON)
        Tools->>HW: Activate Fan
        Control->>State: Update fan_on = True
    end
    
    alt Soil Too Dry
        Control->>Tools: set_water_pump(ON)
        Tools->>HW: Activate Pump
        Control->>State: Update water_pump_on = True
        Control->>State: Update soil_moisture (+15%)
    end
    
    Control->>State: Log Control Actions
    
    State->>Optimize: Trigger Optimization
    
    Optimize->>State: Analyze Logs
    Optimize->>State: Calculate Performance
    Optimize->>State: Adjust Target Parameters
    Optimize->>State: Log Optimization
    
    alt Critical Alert
        State->>Monitor: Reroute to Monitor
    else Normal/Warning
        State->>Start: Cycle Complete
    end
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "Agentic Framework: LangGraph"
        SG[StateGraph]
    end
    
    subgraph "Agent 1: Monitoring"
        MA[MonitoringAgent Class]
        MT1[read_temperature tool]
        MT2[read_humidity tool]
        MT3[read_soil_moisture tool]
        MT4[read_light_level tool]
    end
    
    subgraph "Agent 2: Control"
        CA[ControlAgent Class]
        CT1[set_heater tool]
        CT2[set_fan tool]
        CT3[set_water_pump tool]
        CT4[set_grow_lights tool]
    end
    
    subgraph "Agent 3: Optimization"
        OA[OptimizationAgent Class]
    end
    
    subgraph "State Management"
        GS[GreenhouseState<br/>TypedDict]
        SL[Agent Logs]
        SP[System Parameters]
    end
    
    subgraph "Physical Layer"
        PS[Physical Sensors]
        PA[Physical Actuators]
    end
    
    SG --> MA
    SG --> CA
    SG --> OA
    
    MA --> MT1
    MA --> MT2
    MA --> MT3
    MA --> MT4
    
    CA --> CT1
    CA --> CT2
    CA --> CT3
    CA --> CT4
    
    MA --> GS
    CA --> GS
    OA --> GS
    
    GS --> SL
    GS --> SP
    
    MT1 -.->|Simulated| PS
    MT2 -.->|Simulated| PS
    MT3 -.->|Simulated| PS
    MT4 -.->|Simulated| PS
    
    CT1 -.->|Simulated| PA
    CT2 -.->|Simulated| PA
    CT3 -.->|Simulated| PA
    CT4 -.->|Simulated| PA
    
    style MA fill:#2196F3,color:#ffffff
    style CA fill:#FF9800,color:#ffffff
    style OA fill:#4CAF50,color:#ffffff
    style GS fill:#E91E63,color:#ffffff
    style SG fill:#673AB7,color:#ffffff
```

## State Machine Diagram (State Transitions)

This diagram shows how the GreenhouseState transitions through different states during execution:

```mermaid
stateDiagram-v2
    [*] --> Initialized: System Start
    
    state Initialized {
        temperature: 22.0°C
        humidity: 60.0%
        soil_moisture: 50.0%
        alert_level: normal
    }
    
    Initialized --> Monitoring: Cycle Start
    
    state Monitoring {
        state "Read Sensors" as RS
        state "Update State" as US
        state "Check Alerts" as CA
        
        RS --> US: Sensor Values
        US --> CA: State Updated
        CA --> [*]: Alert Detected
    }
    
    Monitoring --> NormalOperation: Normal/Warning Alert
    Monitoring --> CriticalOperation: Critical Alert
    
    state NormalOperation {
        state "Control Decisions" as CD
        state "Apply Actuators" as AA
        
        CD --> AA: Actions Determined
    }
    
    state CriticalOperation {
        state "Emergency Control" as EC
        state "Immediate Response" as IR
        
        EC --> IR: Critical Actions
    }
    
    NormalOperation --> Optimizing: Control Applied
    CriticalOperation --> Optimizing: Emergency Response
    
    state Optimizing {
        state "Analyze Performance" as AP
        state "Adjust Parameters" as ADP
        
        AP --> ADP: Optimization Needed
        ADP --> [*]: Parameters Updated
    }
    
    Optimizing --> Monitoring: Continue Cycle
    Optimizing --> [*]: Cycle Complete (Normal)
    
    CriticalOperation --> Monitoring: Immediate Re-check
```

## Detailed State Evolution Diagram

This shows how individual state fields change through the workflow:

```mermaid
graph TB
    subgraph "State Initialization"
        SI[temperature: 22.0<br/>humidity: 60.0<br/>soil_moisture: 50.0<br/>light_level: 5000.0<br/>all_actuators: OFF<br/>alert_level: normal]
    end
    
    subgraph "After Monitoring Agent"
        AM[temperature: 21.5<br/>humidity: 65.2<br/>soil_moisture: 48.3<br/>light_level: 3500.0<br/>timestamp: updated<br/>alert_level: normal/warning/critical]
    end
    
    subgraph "After Control Agent"
        AC[temperature: 21.5<br/>humidity: 65.2<br/>soil_moisture: 63.3<br/>light_level: 3500.0<br/>heater_on: TRUE<br/>fan_on: FALSE<br/>water_pump_on: TRUE<br/>grow_lights_on: TRUE]
    end
    
    subgraph "After Optimization Agent"
        AO[temperature: 21.5<br/>humidity: 65.2<br/>soil_moisture: 63.3<br/>light_level: 3500.0<br/>all_actuators: updated<br/>target_temperature: 24.5<br/>target_humidity: 65.0<br/>target_soil_moisture: 60.0<br/>logs: appended]
    end
    
    SI -->|Monitoring Agent<br/>Updates Sensors| AM
    AM -->|Control Agent<br/>Updates Actuators| AC
    AC -->|Optimization Agent<br/>Updates Targets| AO
    AO -->|Next Cycle| SI
    
    style SI fill:#9C27B0,color:#ffffff
    style AM fill:#2196F3,color:#ffffff
    style AC fill:#FF9800,color:#ffffff
    style AO fill:#4CAF50,color:#ffffff
```
