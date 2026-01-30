"""
Job State Service
"""

from sqlalchemy.orm import Session
from src.services.storage import JobDB
from datetime import datetime

def transition_state(db: Session, job_id: str, new_state: str, reason: str = ""):
    """
    Transition job state and log transition
    """
    job = JobDB.get_job(db, job_id)
    if not job:
        return
        
    old_state = job.state
    job.state = new_state
    
    # Log transition
    transition = {
        "from": old_state,
        "to": new_state,
        "timestamp": datetime.utcnow().isoformat(),
        "reason": reason
    }
    
    if not job.state_transitions:
        job.state_transitions = []
    
    # SQLAlchemy JSON mutation tracking requires reassignment
    transitions = list(job.state_transitions)
    transitions.append(transition)
    job.state_transitions = transitions
    
    db.commit()

def is_terminal_state(state: str) -> bool:
    return state in ["SUCCEEDED", "FAILED", "CANCELLED"]
