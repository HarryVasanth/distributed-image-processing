# 🖼️ Distributed Image Processing

[![CI](https://github.com/HarryVasanth/distributed-image-processing/actions/workflows/ci.yml/badge.svg)](https://github.com/HarryVasanth/distributed-image-processing/actions/workflows/ci.yml)

A small but production-minded demo of **distributed image processing**: a CLI
splits an image into horizontal strips, ships them to Celery workers over
RabbitMQ, and stitches the processed strips back together. Results are returned
through Redis, and optional Flower metrics are written to CSV.

The project started in 2016 as a university experiment and has since been
rebuilt around an installable package, typed configuration, validated tasks,
JSON-only serialisation and a test suite.

## Features

- Nine OpenCV operations — edges, thresholding, scaling, translation, rotation,
  perspective transform, box blur, Gaussian blur and Laplacian.
- Horizontal chunking so large 4K images can be processed by several workers.
- Works locally with one worker or across machines sharing a broker.
- Interactive menu for exploring, plus a scriptable `imageproc` CLI.
- Optional Flower integration that records per-task timings in CSV.
- Secure-by-default JSON task protocol, payload limits and parameter validation.
- Unit tests, Ruff linting/formatting, GitHub Actions and Dependabot.

## Architecture

```mermaid
flowchart LR
    subgraph Client
        CLI["imageproc CLI / menu"]
        Encode["Split image<br/>PNG + base64"]
    end

    Broker[("RabbitMQ<br/>broker")]
    Backend[("Redis<br/>result backend")]
    Flower["Flower<br/>optional metrics"]

    subgraph Workers["Celery worker pool"]
        W1["worker 1"]
        W2["worker N"]
    end

    CLI --> Encode
    Encode -->|"JSON tasks"| Broker
    Broker --> W1
    Broker --> W2
    W1 --> Backend
    W2 --> Backend
    Backend -->|"base64 PNG results"| CLI
    CLI --> Output[("results/ images")]
    Broker -.->|"task events"| Flower
    Backend -.->|"task info"| Flower
```

### Request flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as imageproc client
    participant Q as RabbitMQ
    participant W as Celery workers
    participant R as Redis

    U->>C: image, algorithm, parameters
    C->>C: split into strips, encode PNG/base64
    loop each strip
        C->>Q: task(payload, **params)
        Q->>W: deliver task
        W->>W: decode, validate, process, encode
        W->>R: store result
    end
    C->>R: poll AsyncResult
    R-->>C: base64 PNG strip
    C->>C: vstack strips
    C-->>U: save results/<name>_<algorithm>_processed.<ext>
```

Celery carries only JSON. Images cross the wire as base64-encoded PNGs, never
as pickled objects. That removes Celery's largest remote-code-execution risk.

## Requirements

- Python 3.12+
- RabbitMQ 4 (broker)
- Redis 8 (result backend)
- Flower 2 (optional, for CSV metrics)

Python dependencies are pinned in [`pyproject.toml`](pyproject.toml).

## Quick start

```bash
git clone https://github.com/HarryVasanth/distributed-image-processing.git
cd distributed-image-processing

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

docker compose up -d broker backend   # RabbitMQ + Redis on localhost
celery -A imageproc.celery_app worker --loglevel=INFO --concurrency=4
```

In another terminal:

```bash
# Single image, split across workers
imageproc --image 4K/8/lexus_lc500_2017-3840x2160.jpg --algorithm edge_detection

# Rotate a whole folder without saving intermediates
imageproc --folder 4K/4 --algorithm rotation --param angle=90 --no-save

# Write Flower metrics alongside the images
IMAGEPROC_FLOWER_URL=http://localhost:5555 \
  imageproc --image 4K/1/lexus_lc500_2017-3840x2160.jpg \
  --algorithm smooth_blur --report-dir csvFile

# Interactive menu (no arguments)
imageproc
```

Processed files land in `results/` as
`<stem>_<algorithm>_processed.<ext>`. Use `--results-dir` to change that.

### Running workers on other machines

Every machine only needs the package, OpenCV and network access to the broker
and backend:

```bash
export IMAGEPROC_BROKER_URL=amqp://user:password@broker-host:5672//
export IMAGEPROC_RESULT_BACKEND=redis://backend-host:6379/0
celery -A imageproc.celery_app worker --loglevel=INFO --concurrency=4
```

## CLI reference

```text
imageproc [--image PATH | --folder DIR] --algorithm NAME
          [--param NAME=VALUE ...] [--runs N]
          [--results-dir DIR] [--report-dir DIR] [--flower-url URL]
          [--no-split] [--no-save] [--load-color]
          [--list-algorithms] [--version]
```

| Option          | Default            | Purpose                                           |
| --------------- | ------------------ | ------------------------------------------------- |
| `--image`       | —                  | Process one image.                                |
| `--folder`      | —                  | Process every supported image in a folder.        |
| `--algorithm`   | —                  | Algorithm name (see below).                       |
| `--param`       | algorithm defaults | Repeatable `NAME=VALUE` override.                 |
| `--runs`        | `1`                | Timed repetitions; prints mean/min/max wall time. |
| `--results-dir` | `results`          | Where processed images are written.               |
| `--report-dir`  | disabled           | Where Flower CSV metrics are written.             |
| `--flower-url`  | env                | Override `IMAGEPROC_FLOWER_URL`.                  |
| `--no-split`    | off                | Send the whole image in one task.                 |
| `--no-save`     | off                | Benchmark without writing images.                 |
| `--load-color`  | off                | Load in colour instead of grayscale.              |

## Algorithms

| Name             | Split | Parameters (default)                                     |
| ---------------- | ----- | -------------------------------------------------------- |
| `edge_detection` | ✅    | `sigma=0.33` — Canny threshold spread (0–1).             |
| `thresholding`   | ✅    | `threshold=127`, `max_value=255` — binary threshold.     |
| `scaling`        | ✅    | `scale_x=1.0`, `scale_y` — independent resize factors.   |
| `translation`    | ❌    | `tx=0`, `ty=0` — pixel offset, black border.             |
| `rotation`       | ❌    | `angle=0`, `scale=1.0` — centre rotation.                |
| `perspective`    | ❌    | `src`, `dst` — eight comma-separated coordinates each.   |
| `smooth_average` | ✅    | `kernel_x=5`, `kernel_y=5` — box filter, odd kernels.    |
| `smooth_blur`    | ✅    | `kernel_x=5`, `kernel_y=5` — Gaussian blur, odd kernels. |
| `laplacian`      | ✅    | none — normalised 8-bit derivative.                      |

Operations that alter geometry (`translation`, `rotation`, `perspective`) run on
the whole image, because transforming each strip independently would introduce
seams. `--no-split` also works for the remaining algorithms.

Examples:

```bash
imageproc --image photo.jpg --algorithm thresholding --param threshold=180
imageproc --image photo.jpg --algorithm perspective \
  --param src=0,0,4000,0,0,2000,4000,2000 \
  --param dst=100,100,3900,0,0,2100,4000,2000
imageproc --folder photos --algorithm smooth_blur --param kernel_x=7 --param kernel_y=7 --runs 5
```

## Configuration

| Variable                      | Default                               | Meaning                                  |
| ----------------------------- | ------------------------------------- | ---------------------------------------- |
| `IMAGEPROC_BROKER_URL`        | `amqp://guest:guest@localhost:5672//` | Celery broker.                           |
| `IMAGEPROC_RESULT_BACKEND`    | `redis://localhost:6379/0`            | Celery result backend.                   |
| `IMAGEPROC_FLOWER_URL`        | unset                                 | Enable Flower CSV metrics.               |
| `IMAGEPROC_CHUNKS`            | `8`                                   | Number of strips per image.              |
| `IMAGEPROC_POLL_INTERVAL`     | `0.5`                                 | Seconds between result polls.            |
| `IMAGEPROC_TASK_TIMEOUT`      | `600`                                 | Hard task and client timeout in seconds. |
| `IMAGEPROC_MAX_PAYLOAD_BYTES` | `67108864`                            | Maximum decoded payload size (64 MiB).   |

Numeric variables are validated at startup; invalid values raise a clear error
instead of failing later inside a worker.

## Security notes

- **No pickle.** Tasks and results use JSON only (`task_serializer`,
  `result_serializer` and `accept_content`). Never enable pickle on an
  untrusted broker.
- **Secrets stay in the environment.** Broker credentials are not committed.
- **Bounded payloads.** Base64 payloads are size-checked before decoding to
  limit memory abuse.
- **Validated inputs.** Every task validates types and ranges (sigma, kernels,
  thresholds, scales) instead of trusting the client.
- **Local infrastructure.** `compose.yaml` binds RabbitMQ and Redis to
  `127.0.0.1`. Flower has no authentication by default — keep it on a private
  network or put it behind a reverse proxy with auth.
- **Bounded runtime.** Celery hard/soft time limits and client timeouts prevent
  stuck jobs from occupying workers forever.

## Project layout

```text
imageproc/
  celery_app.py    Celery instance and JSON-safe configuration
  config.py        Environment parsing and validation
  codec.py         PNG <-> base64 transport codec
  operations.py    Pure NumPy/OpenCV operations
  tasks.py         Celery wrappers
  imaging.py       Loading, splitting and saving images
  reporting.py     Flower CSV metrics
  client.py        Processing client, CLI and interactive menu
tests/             Unit tests for codec, operations, storage and CLI logic
compose.yaml       Local RabbitMQ + Redis
```

## Development

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

The test suite does not need a broker: operations and task wrappers are tested
locally, while the client is exercised with fake Celery results.

## License

[MIT](LICENSE.md)
