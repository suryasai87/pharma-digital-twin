"""
Operator Training Simulator API
Provides a safe environment for training without affecting real batches
"""
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from backend.utils.auth import verify_token, AuditContext
import random

router = APIRouter()


# In-memory simulator sessions
simulator_sessions: Dict[str, dict] = {}


@router.post("/create-session", response_model=dict)
async def create_simulator_session(
    scenario: str = Body(..., description="Training scenario: contamination, deviation, maintenance"),
    difficulty: str = Body("medium", description="easy, medium, hard"),
    auth: AuditContext = Depends(verify_token)
):
    """
    Create a new training simulator session
    """
    session_id = f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    scenarios = {
        "contamination": {
            "title": "Contamination Response Training",
            "description": "Respond to contamination alert in BR-SIM-01",
            "initial_conditions": {
                "bioreactor": "BR-SIM-01",
                "batch_id": "SIM-BATCH-001",
                "current_phase": "exponential",
                "contamination_risk": 0.85,
                "time_to_respond_minutes": 30
            },
            "objectives": [
                "Identify contamination source",
                "Isolate affected bioreactor",
                "Initiate sampling protocol",
                "Document deviation",
                "Notify QA team"
            ],
            "correct_actions": [
                "stop_feeding",
                "increase_sampling_frequency",
                "create_deviation_report",
                "notify_qa",
                "prepare_batch_disposal"
            ]
        },
        "deviation": {
            "title": "Process Deviation Management",
            "description": "Handle temperature excursion event",
            "initial_conditions": {
                "bioreactor": "BR-SIM-02",
                "batch_id": "SIM-BATCH-002",
                "temperature": 38.5,
                "target_temperature": 37.0,
                "duration_minutes": 15
            },
            "objectives": [
                "Assess impact on product quality",
                "Document deviation with timestamps",
                "Determine if batch can continue",
                "Complete investigation form",
                "Get QA approval to proceed"
            ],
            "correct_actions": [
                "record_exact_temperature_and_time",
                "check_historical_data",
                "assess_impact_on_yield",
                "create_deviation",
                "request_qa_review"
            ]
        },
        "maintenance": {
            "title": "Predictive Maintenance Response",
            "description": "Respond to critical equipment health alert",
            "initial_conditions": {
                "equipment": "Centrifuge-SIM-01",
                "health_score": 62,
                "vibration_level": 4.8,
                "active_batches_affected": 2
            },
            "objectives": [
                "Assess equipment condition",
                "Plan maintenance window",
                "Minimize batch impact",
                "Coordinate with maintenance team",
                "Update equipment records"
            ],
            "correct_actions": [
                "schedule_immediate_inspection",
                "plan_batch_transfer",
                "notify_maintenance",
                "create_work_order",
                "update_equipment_status"
            ]
        }
    }

    if scenario not in scenarios:
        raise HTTPException(status_code=400, detail=f"Invalid scenario. Choose from: {list(scenarios.keys())}")

    session_config = scenarios[scenario]
    session_config["difficulty"] = difficulty
    session_config["created_at"] = datetime.now().isoformat()
    session_config["created_by"] = auth.user_name
    session_config["status"] = "active"
    session_config["score"] = 0
    session_config["actions_taken"] = []
    session_config["time_elapsed_minutes"] = 0

    simulator_sessions[session_id] = session_config

    return {
        "session_id": session_id,
        "scenario": session_config,
        "message": "Simulator session created. Begin training!"
    }


@router.get("/{session_id}/status", response_model=dict)
async def get_simulator_status(
    session_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get current status of simulator session
    """
    if session_id not in simulator_sessions:
        raise HTTPException(status_code=404, detail="Simulator session not found")

    session = simulator_sessions[session_id]

    # Calculate progress
    total_objectives = len(session["objectives"])
    completed_objectives = sum(
        1 for action in session["actions_taken"]
        if action["action"] in session["correct_actions"]
    )
    progress_percent = (completed_objectives / total_objectives * 100) if total_objectives > 0 else 0

    return {
        "session_id": session_id,
        "status": session["status"],
        "progress_percent": round(progress_percent, 1),
        "score": session["score"],
        "time_elapsed_minutes": session["time_elapsed_minutes"],
        "objectives_completed": f"{completed_objectives}/{total_objectives}",
        "actions_taken": len(session["actions_taken"]),
        "current_conditions": session["initial_conditions"]
    }


@router.post("/{session_id}/action", response_model=dict)
async def perform_simulator_action(
    session_id: str,
    action: str = Body(..., description="Action to perform"),
    parameters: dict = Body({}, description="Action parameters"),
    auth: AuditContext = Depends(verify_token)
):
    """
    Perform an action in the simulator
    """
    if session_id not in simulator_sessions:
        raise HTTPException(status_code=404, detail="Simulator session not found")

    session = simulator_sessions[session_id]

    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    # Record action
    action_record = {
        "action": action,
        "parameters": parameters,
        "timestamp": datetime.now().isoformat(),
        "performed_by": auth.user_name
    }
    session["actions_taken"].append(action_record)
    session["time_elapsed_minutes"] += random.randint(1, 5)

    # Evaluate action
    is_correct = action in session["correct_actions"]
    points_earned = 0

    if is_correct:
        points_earned = 20 if session["difficulty"] == "hard" else 15 if session["difficulty"] == "medium" else 10
        session["score"] += points_earned
        feedback = f"✓ Correct action! You earned {points_earned} points."
        outcome = "positive"
    else:
        points_earned = -5
        session["score"] += points_earned
        feedback = f"✗ Incorrect action. {abs(points_earned)} points deducted. Consider the objectives."
        outcome = "negative"

    # Simulate consequences
    consequences = {
        "stop_feeding": "Feed pump stopped. Nutrient levels will stabilize.",
        "increase_sampling_frequency": "Sampling increased to every 2 hours. More data available.",
        "create_deviation_report": "Deviation DEV-SIM-001 created. QA notified.",
        "notify_qa": "QA team alerted. Response expected in 15 minutes.",
        "record_exact_temperature_and_time": "Deviation documented: 38.5°C at 14:23. Timestamp recorded.",
        "schedule_immediate_inspection": "Maintenance team scheduled for immediate inspection.",
        "plan_batch_transfer": "Transfer plan initiated. Backup equipment identified."
    }

    consequence = consequences.get(action, "Action executed.")

    # Check if session complete
    correct_actions_taken = [a["action"] for a in session["actions_taken"] if a["action"] in session["correct_actions"]]
    all_correct_actions_done = all(ca in correct_actions_taken for ca in session["correct_actions"])

    if all_correct_actions_done:
        session["status"] = "completed"
        final_message = f"🎉 Training complete! Final score: {session['score']}"
    else:
        final_message = None

    return {
        "action": action,
        "is_correct": is_correct,
        "points_earned": points_earned,
        "total_score": session["score"],
        "feedback": feedback,
        "consequence": consequence,
        "outcome": outcome,
        "session_status": session["status"],
        "final_message": final_message
    }


@router.get("/{session_id}/summary", response_model=dict)
async def get_simulator_summary(
    session_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get training session summary and performance evaluation
    """
    if session_id not in simulator_sessions:
        raise HTTPException(status_code=404, detail="Simulator session not found")

    session = simulator_sessions[session_id]

    correct_actions = [a for a in session["actions_taken"] if a["action"] in session["correct_actions"]]
    incorrect_actions = [a for a in session["actions_taken"] if a["action"] not in session["correct_actions"]]

    # Calculate performance grade
    score = session["score"]
    if score >= 80:
        grade = "A - Excellent"
    elif score >= 60:
        grade = "B - Good"
    elif score >= 40:
        grade = "C - Satisfactory"
    else:
        grade = "D - Needs Improvement"

    return {
        "session_id": session_id,
        "scenario": session["title"],
        "difficulty": session["difficulty"],
        "status": session["status"],
        "final_score": score,
        "grade": grade,
        "time_elapsed_minutes": session["time_elapsed_minutes"],
        "total_actions": len(session["actions_taken"]),
        "correct_actions": len(correct_actions),
        "incorrect_actions": len(incorrect_actions),
        "objectives_completed": f"{len(correct_actions)}/{len(session['objectives'])}",
        "performance_summary": {
            "strengths": ["Quick response time", "Correct deviation documentation"] if len(correct_actions) > 2 else [],
            "areas_for_improvement": ["Consider sampling frequency", "Complete all checklists"] if len(incorrect_actions) > 1 else []
        },
        "recommended_next_training": "Advanced contamination scenarios" if score >= 70 else "Repeat current scenario"
    }


@router.delete("/{session_id}", response_model=dict)
async def delete_simulator_session(
    session_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Delete a simulator session
    """
    if session_id in simulator_sessions:
        del simulator_sessions[session_id]
        return {"message": "Simulator session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Simulator session not found")
