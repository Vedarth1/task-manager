from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from schemas import TaskCreate,TaskOut
from models import Base,User,Task
from auth import get_current_user
from auth import get_db
from datetime import datetime, timedelta
from typing import List
from datetime import timezone

router = APIRouter()

def send_email_reminder(task_title: str, email: str):
    print(f"Reminder: Task '{task_title}' is due soon! Send to: {email}")

@router.post("/tasks/", response_model=TaskOut)
def create_task(task: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = Task(**task.dict(), created_by=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    if task.due_date - datetime.now(timezone.utc) < timedelta(days=1):
        user = db.query(User).filter(User.id == task.assigned_to).first()
        if user:
            background_tasks.add_task(send_email_reminder, task.title, user.email)
    return db_task

@router.get("/tasks/", response_model=List[TaskOut])
def read_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return db.query(Task).all()
    elif current_user.role == "manager":
        return db.query(Task).filter(Task.assigned_to == current_user.id).all()
    else:
        return db.query(Task).filter(Task.created_by == current_user.id).all()
