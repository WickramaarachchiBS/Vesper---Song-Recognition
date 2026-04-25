# Mobile App Integration Guide

## 📱 How to Connect Your Mobile App to the Server

### Overview

Your mobile app needs to:

1. Record or select an audio clip
2. Extract peak features on-device (primary path)
3. Send peaks as JSON to the backend
4. Fallback to audio upload when needed
5. Receive the recognition result

---

## 🔌 API Endpoints

### Primary Endpoint (Recommended)

```
POST http://YOUR_SERVER_IP:8000/api/identify-peaks
```

Headers:

```
Content-Type: application/json
```

Request body:

```json
{
  "schema_version": "1.0",
  "clip_duration_seconds": 10.0,
  "sample_rate_hz": 44100,
  "hop_size": 512,
  "window_size": 4096,
  "peaks": [
    { "freq_idx": 123, "time_idx": 456 },
    { "freq_idx": 98, "time_idx": 462 }
  ],
  "client_meta": {
    "platform": "android",
    "app_version": "1.0.0"
  }
}
```

Notes:

- `sample_rate_hz`, `hop_size`, and `window_size` must match backend settings.
- `peaks` must be a non-empty list.

### Fallback Endpoint (Compatibility)

```
POST http://YOUR_SERVER_IP:8000/api/identify
```

**Replace `YOUR_SERVER_IP` with:**

- `localhost` or `127.0.0.1` - if testing on same machine
- `192.168.x.x` - if testing on local network (find your PC's IP)
- `your-domain.com` - if deployed to production server

---

## 📤 Request Format

### Fallback Headers

```
Content-Type: multipart/form-data
```

### Fallback Body

- **Field name**: `audio_file`
- **File type**: MP3, WAV, FLAC, OGG, or M4A
- **Recommended**: 10-30 seconds of audio

---

## 📥 Response Format

### Success Response

```json
{
  "success": true,
  "song_id": 1,
  "title": "Song Name",
  "artist": "Artist Name",
  "match_count": 127,
  "confidence": 85.32,
  "total_fingerprints": 149
}
```

### No Match Response

```json
{
  "success": false,
  "message": "No matching song found in database"
}
```

### Error Response

```json
{
  "detail": "Error message here"
}
```

---

## 📱 Platform-Specific Examples

### React Native / Expo (Peak-Based Primary)

```javascript
async function recognizeFromPeaks(peaksPayload) {
  const response = await fetch(
    "http://YOUR_SERVER_IP:8000/api/identify-peaks",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(peaksPayload),
    },
  );

  return response.json();
}
```

### React Native / Expo

```javascript
async function recognizeSong(audioUri) {
  const formData = new FormData();
  formData.append("audio_file", {
    uri: audioUri,
    type: "audio/mp3",
    name: "recording.mp3",
  });

  try {
    const response = await fetch("http://YOUR_SERVER_IP:8000/api/identify", {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    const result = await response.json();

    if (result.success) {
      console.log(`Found: ${result.title} by ${result.artist}`);
      console.log(`Confidence: ${result.confidence}%`);
    } else {
      console.log("Song not found");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}
```

### Flutter

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> recognizeSong(String audioFilePath) async {
  var uri = Uri.parse('http://YOUR_SERVER_IP:8000/api/identify');
  var request = http.MultipartRequest('POST', uri);

  request.files.add(
    await http.MultipartFile.fromPath('audio_file', audioFilePath)
  );

  try {
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    var result = json.decode(responseData);

    if (result['success']) {
      print('Found: ${result['title']} by ${result['artist']}');
      print('Confidence: ${result['confidence']}%');
    } else {
      print('Song not found');
    }
  } catch (e) {
    print('Error: $e');
  }
}
```

### Android (Kotlin)

```kotlin
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import java.io.File

fun recognizeSong(audioFile: File) {
    val client = OkHttpClient()

    val requestBody = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart(
            "audio_file",
            audioFile.name,
            RequestBody.create("audio/mp3".toMediaType(), audioFile)
        )
        .build()

    val request = Request.Builder()
        .url("http://YOUR_SERVER_IP:8000/api/identify")
        .post(requestBody)
        .build()

    client.newCall(request).execute().use { response ->
        val result = JSONObject(response.body?.string() ?: "")

        if (result.getBoolean("success")) {
            val title = result.getString("title")
            val artist = result.getString("artist")
            val confidence = result.getDouble("confidence")

            println("Found: $title by $artist")
            println("Confidence: $confidence%")
        } else {
            println("Song not found")
        }
    }
}
```

### iOS (Swift)

```swift
import Foundation

func recognizeSong(audioFileURL: URL) {
    let url = URL(string: "http://YOUR_SERVER_IP:8000/api/identify")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

    var data = Data()

    // Add audio file
    data.append("--\(boundary)\r\n".data(using: .utf8)!)
    data.append("Content-Disposition: form-data; name=\"audio_file\"; filename=\"recording.mp3\"\r\n".data(using: .utf8)!)
    data.append("Content-Type: audio/mp3\r\n\r\n".data(using: .utf8)!)
    data.append(try! Data(contentsOf: audioFileURL))
    data.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

    request.httpBody = data

    URLSession.shared.dataTask(with: request) { data, response, error in
        guard let data = data,
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return
        }

        if let success = json["success"] as? Bool, success {
            let title = json["title"] as? String ?? ""
            let artist = json["artist"] as? String ?? ""
            let confidence = json["confidence"] as? Double ?? 0

            print("Found: \(title) by \(artist)")
            print("Confidence: \(confidence)%")
        } else {
            print("Song not found")
        }
    }.resume()
}
```

---

## 🧪 Testing the Connection

### 1. Find Your Server IP

**Windows:**

```bash
ipconfig
# Look for IPv4 Address under your network adapter
```

**Mac/Linux:**

```bash
ifconfig
# or
ip addr show
```

### 2. Test from Mobile Device

Make sure:

- ✅ Server is running: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- ✅ Mobile device is on same WiFi network
- ✅ Firewall allows port 8000

### 3. Quick Test with Browser

On your mobile device, open browser and visit:

```
http://YOUR_SERVER_IP:8000
```

You should see the API welcome message.

---

## 🔒 Production Deployment

For production, you should:

1. **Use HTTPS** (not HTTP)
2. **Deploy to cloud server** (AWS, Google Cloud, Azure, etc.)
3. **Use domain name** instead of IP address
4. **Add authentication** if needed
5. **Rate limiting** to prevent abuse

Example production URL:

```
https://api.vesper-music.com/api/identify
```

---

## 💡 Tips for Mobile App

### Audio Recording

- **Duration**: 10-30 seconds is optimal
- **Quality**: Higher quality = better recognition
- **Format**: MP3 or WAV recommended
- **Sample rate**: 44.1 kHz or higher

### User Experience

- Show loading indicator while processing
- Display confidence score to user
- Handle "not found" gracefully
- Cache results to avoid duplicate requests

### Error Handling

```javascript
// Example error handling
try {
  const result = await recognizeSong(audioUri);

  if (result.success) {
    if (result.confidence > 70) {
      // High confidence - show result
      showResult(result);
    } else {
      // Low confidence - ask user to try again
      showLowConfidenceWarning();
    }
  } else {
    // Not found
    showNotFoundMessage();
  }
} catch (error) {
  // Network or server error
  showErrorMessage("Unable to connect to server");
}
```

---

## 📊 Response Fields Explained

| Field                | Type    | Description                             |
| -------------------- | ------- | --------------------------------------- |
| `success`            | boolean | `true` if song found, `false` otherwise |
| `song_id`            | integer | Database ID of the song                 |
| `title`              | string  | Song title                              |
| `artist`             | string  | Artist name                             |
| `match_count`        | integer | Number of matching fingerprints         |
| `confidence`         | float   | Confidence score (0-100%)               |
| `total_fingerprints` | integer | Total fingerprints in query             |
| `message`            | string  | Error/info message (when success=false) |

---

## ❓ Troubleshooting

### "Network request failed"

- Check server is running
- Verify IP address is correct
- Ensure mobile device is on same network
- Check firewall settings

### "Connection refused"

- Server might not be running
- Wrong port number
- Server not listening on 0.0.0.0

### "Song not found" but should be in database

- Check song was actually added to database
- Try longer audio clip (15-30 seconds)
- Ensure good audio quality
- Check for background noise

### Slow response

- Large file size - compress audio before sending
- Server processing time - normal for first request
- Network speed - use WiFi instead of cellular

---

## 🚀 Next Steps

1. Start the server
2. Test with browser first
3. Implement in your mobile app
4. Test with sample audio
5. Deploy to production when ready
