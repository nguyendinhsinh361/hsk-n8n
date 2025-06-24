## Audio Splitting API

### Split Single Audio

This endpoint allows you to split a single audio file into segments based on provided timestamps.

**Endpoint**: `POST /audio/split-single`

**Request Body**:
```json
{
  "audio_link": "https://drive.google.com/file/d/1abcdefghijklmnopqrstuvwxyz/view",
  "timestamps": [
    ["00:00:00", "00:01:30"],
    ["00:01:45", "00:03:20"]
  ],
  "key": "unique_audio_identifier",
  "output_directory": "app/data/split/" // Optional
}
```

**Response**:
```json
{
  "key": "unique_audio_identifier",
  "audio_file": "unique_audio_identifier.mp3",
  "file_path": "app/data/split/unique_audio_identifier.mp3",
  "success": true
}
```

**Example Usage**:
```python
import requests

url = "http://localhost:8000/audio/split-single"
payload = {
  "audio_link": "https://drive.google.com/file/d/1abcdefghijklmnopqrstuvwxyz/view",
  "timestamps": [
    ["00:00:00", "00:01:30"],
    ["00:01:45", "00:03:20"]
  ],
  "key": "unique_audio_identifier"
}

response = requests.post(url, json=payload)
print(response.json())
```
