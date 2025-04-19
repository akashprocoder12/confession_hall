from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Confession, Comment, Like
from bson import ObjectId
from typing import List

from pymongo import MongoClient

client = MongoClient("mongodb+srv://proversionofakash:yXmPmDDhLvZfSx62@cluster0.eiefq2m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.confessionDB
confessions = db.confessions

app = FastAPI()

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def confession_serializer(c):
    return {
        "id": str(c["_id"]),
        "text": c["text"],
        "tags": c.get("tags", []),
        "likes": c.get("likes", 0),
        "comments": c.get("comments", [])
    }

@app.get("/confessions", response_model=List[dict])
def get_confessions():
    return [confession_serializer(c) for c in confessions.find().sort("_id", -1)]

@app.post("/confessions")
def post_confession(conf: Confession):
    result = confessions.insert_one({
        "text": conf.text,
        "tags": conf.tags,
        "likes": 0,
        "comments": []
    })
    return {"id": str(result.inserted_id)}

@app.post("/like")
def toggle_like(like: Like):
    conf = confessions.find_one({"_id": ObjectId(like.confession_id)})
    if not conf:
        raise HTTPException(status_code=404, detail="Confession not found")

    current_likes = conf.get("likes", 0)
    
    if like.action == "like":
        new_likes = current_likes + 1
    else:
        new_likes = max(0, current_likes - 1)

    confessions.update_one(
        {"_id": ObjectId(like.confession_id)},
        {"$set": {"likes": new_likes}}
    )
    return {"likes": new_likes}

@app.post("/comment")
def add_comment(comment: Comment):
    confessions.update_one(
        {"_id": ObjectId(comment.confession_id)},
        {"$push": {"comments": comment.comment}}
    )
    return {"status": "Comment added"}
