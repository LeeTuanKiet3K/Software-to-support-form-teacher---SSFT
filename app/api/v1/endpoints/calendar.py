from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel

from app.api.deps import get_calendar_service
from app.services.CalendarService import CalendarService

router = APIRouter()

class EventResponse(BaseModel):
    id: str
    title: str
    date: int
    time: str
    location: str
    type: str

class EventsListResponse(BaseModel):
    events: List[EventResponse]

class CreateEventRequest(BaseModel):
    title: str
    date: int
    time: str
    location: str
    type: str
    user_id: Optional[str] = "GVCN" # Giả lập user_id cho đơn giản

class CreateEventResponse(BaseModel):
    success: bool
    event_id: str
    message: str

@router.get("/events", response_model=EventsListResponse)
async def get_events(calendar_service: CalendarService = Depends(get_calendar_service)):
    """Lấy danh sách tất cả sự kiện"""
    raw_events = calendar_service.get_all_events()
    events_list = []
    
    for ev in raw_events:
        events_list.append(EventResponse(
            id=ev.get("id", ""),
            title=ev.get("title", ""),
            date=int(ev.get("date", 0)),
            time=ev.get("time", ""),
            location=ev.get("location", ""),
            type=ev.get("type", "event")
        ))
        
    return EventsListResponse(events=events_list)

@router.post("/events", response_model=CreateEventResponse, status_code=201)
async def create_event(
    payload: CreateEventRequest,
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """Tạo mới một sự kiện"""
    event_id = calendar_service.create_event(
        title=payload.title,
        date=str(payload.date),
        time=payload.time,
        location=payload.location,
        event_type=payload.type,
        user_id=payload.user_id or "GVCN"
    )
    
    if not event_id:
        raise HTTPException(status_code=500, detail="Không thể tạo sự kiện.")
        
    return CreateEventResponse(
        success=True,
        event_id=event_id,
        message="Tạo sự kiện thành công."
    )

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str = Path(...),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """Xóa sự kiện"""
    success = calendar_service.delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy sự kiện để xóa.")
        
    return {"success": True, "message": "Đã xóa sự kiện"}
