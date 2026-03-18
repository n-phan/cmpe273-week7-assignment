# CMPE273 Week 7 - Microservice Discovery

This is a simple demonstration of service discovery:
- A `registry` service stores instance URLs in memory.
- Two `service` instances register themselves on startup.
- A `client` discovers registered instances and calls a random one.

## Run

From this directory:

```bash
docker compose up --build
```

The `client` container runs once and prints:
- the discovered instance URLs
- which instance was chosen randomly
- the response from that instance

## How to run client again

In another terminal:

```bash
docker compose run --rm client
```

#### Sample Output

Because the client picks a random instance, the `Chosen random instance` and `Worker response.instance_id` may be `service1` or `service2`.

```text
Discovered instance URLs: ['http://service1:8000', 'http://service2:8000']
Chosen random instance: http://service2:8000
Worker response: {'service_name': 'demo-service', 'instance_id': 'service2', 'random_result': 483921, 'server_time': 1700000000.123}
```
<img width="3164" height="2074" alt="image" src="https://github.com/user-attachments/assets/22dc5294-b7ca-4993-9544-81a6c96052a8" />

