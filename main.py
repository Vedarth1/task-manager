from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends ,HTTPException
from models import Base,User
from schemas import UserCreate,Token
from tasks import router
from database import engine
from auth import get_db,get_password_hash,OAuth2PasswordRequestForm,verify_password,create_access_token
from sqlalchemy.orm import Session
from websocket import ConnectionManager

manager = ConnectionManager()

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)

@app.post("/auth/signup")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User created"}

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message text was: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
