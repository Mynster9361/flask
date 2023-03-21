from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import uuid
import os
import shutil


app = FastAPI()
print(os.path)
@app.post("/to/")
async def create_upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]  # Get the file extension
    new_filename = f"{str(uuid.uuid4())}.{file_ext}"
    file_path = os.path.join("/app/src/files/to", new_filename)  # Set the file path
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    return {"filename": new_filename}


@app.get("/from/{filename}")
def download_file(filename: str):
    download_dir = "/app/src/files/from"
    completed_dir = "/app/src/files/from_completed"
    file_path = os.path.join(download_dir, filename)
    completed_file_path = os.path.join(completed_dir, filename)
    if os.path.exists(completed_file_path):
        return FileResponse(completed_file_path, filename=filename)
    elif os.path.exists(file_path):
        shutil.move(file_path, completed_file_path)
        return FileResponse(completed_file_path, filename=filename)
    else:
        return {"message": "File not found."}
    
@app.get("/from/")
async def list_available_files():
    download_dir = "/app/src/files/from"
    filenames = os.listdir(download_dir)
    return {"files": filenames}
