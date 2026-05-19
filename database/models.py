"""
Database models for Re:Gain Bot
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    matric_number: str
    full_name: Optional[str] = None
    total_tokens: int = 0
    starpoint_eligible: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Submission:
    submission_id: int
    user_id: int
    category: str  # 'reuse', 'recycle_plastics', 'recycle_cans', 'recycle_paper', 'reduce'
    photo_file_id: str
    tokens_awarded: int
    status: str  # 'pending', 'approved', 'rejected'
    created_at: datetime = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AdminVerification:
    verification_id: int
    submission_id: int
    admin_id: int
    decision: str  # 'approved', 'rejected'
    reason: Optional[str] = None
    verified_at: datetime = None
    
    def __post_init__(self):
        if self.verified_at is None:
            self.verified_at = datetime.now()
