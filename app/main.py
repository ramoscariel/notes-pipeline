from fastapi import FastAPI, HTTPException, Request
from app.crud import create_note, get_note_by_id, get_notes, delete_note
from app.models import Note, NoteCreate
from app.launchdarkly_config import ld_client

# Hola mundo!
app = FastAPI(title="Notes API")


@app.on_event("startup")
async def startup_event():
    ld_client.initialize()


@app.post("/notes", response_model=Note)
def create(note: NoteCreate, request: Request):
    user_id = request.headers.get("X-User-Id", request.client.host)
    context = ld_client.create_context(user_id)

    enable_note_creation = ld_client.get_flag(
        "enable-note-creation", context, True
    )

    if not enable_note_creation:
        raise HTTPException(
            status_code=503, detail="Note creation is temporarily disabled"
        )

    return create_note(note)


@app.get("/notes", response_model=list[Note])
def list_notes(request: Request):
    user_id = request.headers.get("X-User-Id", request.client.host)
    context = ld_client.create_context(user_id)

    enable_advanced_filtering = ld_client.get_flag(
        "enable-advanced-filtering", context, False
    )

    notes = get_notes()

    if enable_advanced_filtering:
        notes = sorted(notes, key=lambda x: x.id, reverse=True)

    return notes


@app.get("/notes/{note_id}", response_model=Note)
def get(note_id: int):
    note = get_note_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.delete("/notes/{note_id}")
def delete(note_id: int, request: Request):
    user_id = request.headers.get("X-User-Id", request.client.host)
    context = ld_client.create_context(user_id)

    enable_note_deletion = ld_client.get_flag(
        "enable-note-deletion", context, True
    )

    if not enable_note_deletion:
        raise HTTPException(
            status_code=503, detail="Note deletion is temporarily disabled"
        )

    deleted = delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"deleted": True}


@app.on_event("shutdown")
async def shutdown_event():
    ld_client.close()
