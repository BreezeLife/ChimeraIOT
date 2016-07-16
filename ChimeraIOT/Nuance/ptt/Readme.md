# SNORE - Speech daemoN On Rasperry piE

The speech daemon, snore, is a service that uses PortAudio and Nuance connected
services to provide speech recognition, NLU and speech synthesis via a simple
HTTP interface. The audio handling is completely managed by the service so that
the user only needs to make a single HTTP GET or POST via curl, requests, or
any other HTTP client to integrate with speech services.

## Installation

Snore is a Python application that uses some basic binary libraries for audio
handling and speech coding.  There are some prerequisites that must be installed
prior to configuring and running the service.

    sudo apt-get install libspeex-dev libspeexdsp-dev portaudio19-dev \
        libffi-dev python3-dev

Install the required Python packages.

    pip install -r requirements.txt

## Running the service

The service is a simple web server that should be run in the background or as a
system service.

    python snore/server.py &

## Using the service

The snore service provides three endpoints, one for each speech service:

* /asr: Perform speech recognition, returning a transcription
* /nlu: Perform NLU, returning a transacription and interpretation
* /tts: Perform speech synthesis by sending text

Each service requires a number of parameters including credentials and service
configuration.  The parameters may be sent as HTTP headers or query parameters.
Credentials and other configuration values may be retrieved from the Nuance
Developers site at https://developer.nuance.com.

All services require the following credentials to be sent:

* app_id: A developer application ID
* key: The 128 character application key

In addition, all services require the following configuration parameters:

* user_id: A string value identifying the current user speaking
* language: The language code, for example: eng-USA

The request will last the duration of the entire service transaction. So in the
case of basic speech recognition, the HTTP request will not complete until the
user finishes speaking and the speech service returns a transcription. The
response is streaming via chunked transfer encoding to provide real-time
updates regarding the status of the transaction. For speech recognition, you
will receive a JSON response when the user finishes speaking and then when the
transcription is returned. In case there is an error, that will also be sent as
a JSON result chunk with a descriptive message to explain the error.

### Speech recognition

The `/asr` endpoint provides speech recognition. In addition to the general
parameters, ASR also requires the dictation type:

* dictation_type: The speech recognition model to use

Request speech recognition using curl:

```bash
curl -v localhost:8080/asr -N \
    -H 'NMSP_APPID: <APP_ID>' \
    -H 'NMSP_KEY: <APP_KEY>' \
    -H 'NMSP_USER: username' \
    -H 'NMSP_LANGUAGE: eng-USA' \
    -H 'NMSP_RECOGNITION_TYPE: dictation'
```

This will block until the user finishes speaking and return a JSON chunk
indicating that speech has ended:

```json
{"audio_state": "complete", "result_format": "audio"}
```

Followed by a JSON message containing the transcription and detailed results:

```json
{"cadence_regulatable_result": "completeRecognition", "confidences": [458, 0, 0], "NMAS_PRFX_TRANSACTION_ID": "0", "result_format": "rec_text_results", "NMAS_PRFX_SESSION_ID": "70a0a2c8-4282-430e-bca6-20ae556c45c3", "message": "query_response", "result_type": "NVC_ASR_CMD", "prompt": "", "transaction_id": 0, "status_code": 0, "final_response": 1, "audio_transfer_info": {"end_time": "20160714100657035", "packages": [{"bytes": 640, "time": "20160714100654784"}, {"bytes": 640, "time": "20160714100657035"}], "start_time": "20160714100654370", "nss_server": "172.16.59.226:4514", "audio_id": 0}, "transcriptions": ["Let's start hacking", "Let's start having", "Let's start packing"], "words": [[{"word": "Let's\\*no-space-before", "confidence": "0.933"}, {"word": "start", "confidence": "0.893"}, {"word": "hacking", "confidence": "0.462"}], [{"word": "Let's\\*no-space-before", "confidence": "0.0"}, {"word": "start", "confidence": "0.0"}, {"word": "having", "confidence": "0.0"}], [{"word": "Let's\\*no-space-before", "confidence": "0.0"}, {"word": "start", "confidence": "0.0"}, {"word": "packing", "confidence": "0.0"}]]}
```

Ending with a message indicating the transaction is complete:

```json
{"message": "query_end", "transaction_id": 0}
```

### NLU

The `/nlu` endpoint provides access to Mix natural language understanding and
requires that a model is configured in Mix and deployed with a tag. The NLU
endpoint requires specifying the tag.

Request NLU using curl:

```bash
curl -v localhost:8080/nlu -N \
    -H 'NMSP_APPID: <APP_ID>' \
    -H 'NMSP_KEY: <APP_KEY>' \
    -H 'NMSP_USER: username' \
    -H 'NMSP_LANGUAGE: eng-USA' \
    -H 'NMSP_TAG: MY_MODEL_TAG_V1'
```

As with ASR, this request will send a speech marker message:

```json
{"audio_state": "complete", "result_format": "audio"}
```

And a transcription:

```json
{"cadence_regulatable_result": "completeRecognition", "confidences": [738, 0, 0], "NMAS_PRFX_TRANSACTION_ID": "0", "result_format": "rec_text_results", "NMAS_PRFX_SESSION_ID": "001d3a02-dd03-4433-84c5-cfc9af164663", "message": "query_response", "result_type": "NDSP_ASR_APP_CMD", "prompt": "", "transaction_id": 0, "status_code": 0, "final_response": 0, "audio_transfer_info": {"end_time": "20160714102000687", "packages": [{"bytes": 640, "time": "20160714101958440"}, {"bytes": 640, "time": "20160714102000688"}], "start_time": "20160714101958020", "audio_id": 0, "nss_server": "172.16.59.229:4505"}, "transcriptions": ["Look at the train", "Look up the train", "Look up a train"], "words": [[{"word": "Look\\*no-space-before", "confidence": "0.977"}, {"word": "at", "confidence": "0.876"}, {"word": "the", "confidence": "0.976"}, {"word": "train", "confidence": "0.974"}], [{"word": "Look\\*no-space-before", "confidence": "0.0"}, {"word": "up", "confidence": "0.0"}, {"word": "the", "confidence": "0.0"}, {"word": "train", "confidence": "0.0"}], [{"word": "Look\\*no-space-before", "confidence": "0.0"}, {"word": "up", "confidence": "0.0"}, {"word": "a", "confidence": "0.0"}, {"word": "train", "confidence": "0.0"}]]}
```

The NLU endpoint will also return an interpretation message:

```json
{"cadence_regulatable_result": "completeRecognition", "NMAS_PRFX_TRANSACTION_ID": "0", "result_format": "nlu_interpretation_results", "NMAS_PRFX_SESSION_ID": "001d3a02-dd03-4433-84c5-cfc9af164663", "message": "query_response", "result_type": "NDSP_ASR_APP_CMD", "prompt": "", "transaction_id": 0, "nlu_interpretation_results": {"status": "success", "payload_format": "nlu-base", "final_response": 1, "payload_version": "1.0", "payload": {"interpretations": [{"action": {"intent": {"confidence": 1.0, "value": "EXAMINE"}}, "concepts": {"THING": [{"ranges": [[12, 17]], "value": "train", "literal": "train"}]}, "literal": "Look at the train"}], "diagnostic_info": {"nlu_language": "eng-USA", "timing": {"intermediateRespSentDelay": "163", "finalRespSentDelay": "124"}, "nmaid": "NMDPPRODUCTION_Nuance_Interactive_Fiction_20160321170301", "nlu_version": "[Version: nlps-eng-USA-QUICKNLU;Label;844_NLPS_6;Model;85432587-7f41-11e5-8c9e-5927901c1883;Build;478814d8-871d-11e5-8c9e-0f6de118dd3a;QnluTrain;1.9.4;CreatedAt;2015-11-09T20:05:37.000Z]", "context_tag": "M844_A1049_V6"}, "type": "nlu-1.0"}}, "status_code": 0, "final_response": 1, "audio_transfer_info": {"end_time": "20160714102000687", "packages": [{"bytes": 640, "time": "20160714101958440"}, {"bytes": 640, "time": "20160714102000688"}], "start_time": "20160714101958020", "audio_id": 0, "nss_server": "172.16.59.229:4505"}}
```

And a final message:

```json
{"message": "query_end", "transaction_id": 0}
```

### TTS

The `/tts` endpoint provides speech synthesis from a text string. This endpoint
requires that the text is POSTed to the server as utf8 text.

Request TTS using curl:

```bash
curl -v localhost:8080/tts -N \
    -H 'NMSP_APPID: <APP_ID>' \
    -H 'NMSP_KEY: <APP_KEY>' \
    -H 'NMSP_USER: username' \
    -H 'NMSP_LANGUAGE: eng-USA' \
    -d "theda thida thida that's all folks"
```

This request returns when the sythesized speech has finished playing.

## Python client

This service is most useful when using it from an application as a web API.
There is a sample of this interaction using requests in Python in the client.py
file.

This file shows how to send the parameters as both headers and query
parameters, how to receive the response a chunk at a time as JSON and how to
POST the text for TTS. This sample is also a basic CLI that provides access to
the speech services.

ASR CLI:

    python client.py asr <APP_ID> <APP_KEY> eng-USA username dictation

NLU CLI:

    python client.py nlu <APP_ID> <APP_KEY> eng-USA username MY_MODEL_TAG_V1

TTS CLI:

    python client.py tts <APP_ID> <APP_KEY> eng-USA username "theda thida thida that's all folks"

