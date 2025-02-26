from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

#Handling Request Bodies with FastAPI:

# Simulated empty database
dummy_database = {}
user_id_counter = 1  # Keeps track of new user IDs


# Full User Model
class User(BaseModel):
    username: str
    email: str
    age: int
    password: str
    is_active: bool


# Partial Update Model (all fields optional)
class PartialUser(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


#CREATE a new user
@app.post("/users/")
async def create_user(user: User):
    global user_id_counter

    # Assign a new user ID and store it in the database
    dummy_database[user_id_counter] = user.model_dump()
    user_id_counter += 1

    return {"message": "User created successfully!", 
            "user_id": user_id_counter - 1, 
            "user": user.model_dump()}


#READ a single user by their ID or all users
@app.get("/users/all")
async def list_users():
    if not dummy_database:
        return {"message": "No users found!", 
                "users": []}
    
    return {"message": f"total users: {len(dummy_database)}", 
            "users": dummy_database} 


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in dummy_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id": user_id, 
            "user": dummy_database[user_id]}
        

#UPDATE user info (partial or overall update)
@app.patch("/users/{user_id}")
async def update_user(user_id: int, user_update: PartialUser):
    if user_id not in dummy_database or not dummy_database[user_id]:
        raise HTTPException(status_code=404, detail="User not found")

    # Get existing user and update only provided fields
    updated_data = user_update.model_dump(exclude_none=True)
    dummy_database[user_id].update(updated_data)

    return {"message": f"User {user_id} updated!", 
            "updated_user": dummy_database[user_id]}


#DELETE a user
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    if user_id not in dummy_database:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_user = dummy_database.pop(user_id)  # Remove user from database

    # Reassign user ID's to fill gaps after deletion
    for remaining_user_id in list(dummy_database.keys()):
        if remaining_user_id > user_id:
            # Shift the ID of users greater than deleted user ID
            dummy_database[remaining_user_id - 1] = dummy_database.pop(remaining_user_id)

    # Update the user_id_counter if necessary
    global user_id_counter
    user_id_counter -= 1

    return {"message": f"User {user_id} deleted!", 
            "deleted_user": deleted_user}
