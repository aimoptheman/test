# Hello World JS App

A minimal Node.js HTTP server built with no external dependencies.

## Requirements

- Node.js >= 18

## Usage

```bash
npm start
```

Server starts on port 3000 by default. Override with the `PORT` environment variable:

```bash
PORT=8080 npm start
```

## Endpoints

| Method | Path      | Response                       |
|--------|-----------|--------------------------------|
| GET    | `/`       | `200 Hello, World!`            |
| GET    | `/health` | `200 { "status": "ok" }`       |
| *      | other     | `404 Not Found`                |
