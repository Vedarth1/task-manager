from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from schemas import TaskCreate,TaskOut,TaskUpdate
from models import Base,User,Task
from auth import get_current_user
from auth import get_db
from datetime import datetime, timedelta
from typing import List
from datetime import timezone
from uuid import UUID
import smtplib,os
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

def send_email_reminder(task_title: str, email: str):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    FROM_PASSWORD = os.getenv("FROM_PASSWORD")

    subject = f"Task Reminder: {task_title}"
    body = f"Hello,\n\nJust a reminder that the task \"{task_title}\" is due soon.\n\nStay productive!\n"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(FROM_EMAIL, FROM_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Reminder sent for task '{task_title}' to {email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


@router.post("/tasks/", response_model=TaskOut)
def create_task(task: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = Task(**task.dict(), created_by=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    if task.due_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc) < timedelta(days=1):
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
    
@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role != "admin" and task.created_by != current_user.id and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role != "admin" and task.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.task_id == task_id, Task.created_by == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task