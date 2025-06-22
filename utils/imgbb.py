import httpx
from fastapi import UploadFile, HTTPException

# Replace with your actual ImgBB API key
IMGBB_API_KEY = "1a4a5157f0f133c2272817cadf6e9d17"

async def upload_image_to_imgbb(file: UploadFile) -> str:
    """
    Uploads an image to ImgBB and returns the URL.
    """
    if not IMGBB_API_KEY or IMGBB_API_KEY == "YOUR_IMGBB_API_KEY":
        raise HTTPException(
            status_code=500,
            detail="ImgBB API key is not configured."
        )

    api_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    
    async with httpx.AsyncClient() as client:
        files = {'image': (file.filename, await file.read(), file.content_type)}
        response = await client.post(api_url, files=files)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image to ImgBB: {response.text}"
        )
        
    data = response.json()
    if not data.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"ImgBB returned an error: {data.get('error', {}).get('message')}"
        )
        
    return data['data']['url']