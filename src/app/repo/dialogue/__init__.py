from app.repo.dialogue.base import IDialogueRepo
from app.repo.dialogue.mongo import DialogueRepo as MongoDBDialogueRepo

dialogue_repo_map = {
    "mongodb": MongoDBDialogueRepo,
}


async def get_dialogue_repo(key: str) -> IDialogueRepo:
    return dialogue_repo_map[key]
