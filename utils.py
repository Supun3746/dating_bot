import json
import os

import cv2
import insightface
import numpy as np
from sqlalchemy import select

from database import Men, Women, db

models = [
    insightface.app.FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider"]),
    insightface.app.FaceAnalysis(
        name="antelopev2", providers=["CUDAExecutionProvider"]
    ),
]

for model in models:
    model.prepare(ctx_id=0)


async def extract_average_embedding(image, to_db=True):
    if isinstance(image, str):
        image = cv2.imread(image)

    if isinstance(image, bytes):
        image_array = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    embeddings = []
    for model in models:
        faces = model.get(image)
        if faces:
            embeddings.append(faces[0].embedding)
    if not embeddings:
        raise ValueError("Лицо не найдено.")

    avg_embedding = np.mean(embeddings, axis=0)

    if to_db:
        avg_embedding_serialized = json.dumps(avg_embedding.tolist())
        return avg_embedding_serialized

    return avg_embedding


async def find_most_similar_user(target_embedding, user_id):
    # image_array = np.frombuffer(target_embedding, np.uint8)
    # input_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # average_embedding = await extract_average_embedding(target_embedding, to_db=False)
    # average_embedding = np.array(json.loads(average_embedding), dtype=np.float32)

    users = await get_gender(user_id)
    return await cosine_similarity(average_embedding=target_embedding, users=users)


async def cosine_similarity(average_embedding, users, n=1):
    similarities = []
    for user in users:
        user_embedding = np.array(json.loads(user.photo_embedding), dtype=np.float32)

        similarity = np.dot(average_embedding, user_embedding) / (
            np.linalg.norm(average_embedding) * np.linalg.norm(user_embedding)
        )
        similarities.append((user, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar_users = similarities[:n]
    return most_similar_users[0][0]


async def get_gender(user_id):
    print(user_id)
    async with db.session_factory() as session:
        result = await session.execute(
            select(Men.find_gender).where(Men.user_id == user_id)
        )

        gender = result.scalar()

        if not gender:
            result = await session.execute(
                select(Women.find_gender).where(Women.user_id == user_id)
            )
            gender = result.scalar()
        print(gender)
        if not gender:
            res = await session.execute(select(Women))
            users = res.scalars().all()
        else:
            res = await session.execute(select(Men))
            users = res.scalars()
        return users
