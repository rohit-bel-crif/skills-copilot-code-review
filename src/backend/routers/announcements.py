"""
Announcement endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..database import db
from ..routers.auth import check_session

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

class Announcement(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    message: str
    start_date: Optional[datetime] = None
    expiration_date: datetime

# Dependency to check if user is signed in

def require_auth(username: str = None):
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Optionally, check session validity here
    return username

@router.get("/", response_model=List[Announcement])
def list_announcements():
    """List all announcements (including expired for management)"""
    return list(db.announcements.find())

@router.post("/", response_model=Announcement)
def create_announcement(announcement: Announcement, username: str = Depends(require_auth)):
    if not announcement.expiration_date:
        raise HTTPException(status_code=400, detail="Expiration date required")
    doc = announcement.dict(by_alias=True, exclude_unset=True)
    result = db.announcements.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc

@router.put("/{announcement_id}", response_model=Announcement)
def update_announcement(announcement_id: str, announcement: Announcement, username: str = Depends(require_auth)):
    doc = announcement.dict(by_alias=True, exclude_unset=True)
    db.announcements.update_one({"_id": announcement_id}, {"$set": doc})
    doc["_id"] = announcement_id
    return doc

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, username: str = Depends(require_auth)):
    db.announcements.delete_one({"_id": announcement_id})
    return {"success": True}
