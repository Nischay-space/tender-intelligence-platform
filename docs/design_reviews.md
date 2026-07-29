# HTTP Client Design Review

## Responsibility

Provide a reusable interface for all network communication.

## Owns

- Sessions
- Timeouts
- Retries
- Headers
- Logging
- Authentication
- Error handling

## Does NOT Own

- HTML parsing
- Database storage
- Duplicate detection
- Business logic

## Public Interface

client.get()

client.post()

client.close()

## Future Enhancements

- Async support
- Rate limiting
- Metrics
- Proxy configuration
- Circuit breaker