def resp_codes(from_code: int, to_code: int) -> frozenset[int]:
    return frozenset(range(from_code, to_code + 1))


# Informational Responses (1xx)
codes_1xx = resp_codes(100, 101)
"""
100 Continue                                – The initial part of a request has been received and the client can continue with the rest.
101 Switching Protocols                     – The server is switching protocols as requested by the client.
"""

# Successful Responses (2xx)
codes_2xx = resp_codes(200, 206)
"""
200 OK                                      – The request was successful.
201 Created                                 – A new resource has been successfully created.
202 Accepted                                – The request has been accepted for processing but not completed.
203 Non-Authoritative Information           – Metadata may be modified from the original.
204 No Content                              – The server successfully processed the request, but there's no content to return.
205 Reset Content                           – Tells the client to reset the document view.
206 Partial Content                         – Only part of the resource was sent (useful for range requests).
"""

# Redirection Messages (3xx) redirect_message
codes_3xx = resp_codes(300, 308)
"""
300 Multiple Choices                        – Multiple options for the resource (e.g., different formats).
301 Moved Permanently                       – Resource has been permanently moved to a new URI.
302 Found                                   – Resource is temporarily located at a different URI.
303 See Other                               – Response can be found under a different URI and should be retrieved using GET.
304 Not Modified                            – Cached version is still valid; no need to resend.
307 Temporary Redirect                      – Resource temporarily moved to another URI; method unchanged.
308 Permanent Redirect                      – Like 301 but method remains unchanged.
"""

# Client Error Responses (4xx) client_error
codes_4xx = resp_codes(400, 412) | frozenset({416, 418, 425, 429, 451})
"""
400 Bad Request                             – The request cannot be processed due to client error.
401 Unauthorized                            – Authentication is required and has failed or not been provided.
402 Payment Required                        – Reserved for future use.
403 Forbidden                               – The server understands but refuses to authorize the request.
404 Not Found                               – The resource could not be found.
405 Method Not Allowed                      – HTTP method is not allowed for the resource.
406 Not Acceptable                          – The requested format is not acceptable.
407 Proxy Authentication Required           – Client must authenticate with a proxy.
408 Request Timeout                         – The server timed out waiting for the request.
409 Conflict                                – Request conflicts with the current state of the server.
410 Gone                                    – The resource has been permanently removed.
411 Length Required                         – Content-Length header is required.
412 Precondition Failed                     – Preconditions in headers were not met.
416 Range Not Satisfiable                   – Range requested cannot be fulfilled.
418 I'm a teapot                            – Joke code from RFC 2324; not implemented in real servers.
425 Too Early                               – Server is unwilling to risk processing a request that might be replayed.
429 Too Many Requests                       – Rate limit exceeded.
451 Unavailable For Legal Reasons           – Resource blocked due to legal demand.
"""

# Server Error Responses (5xx)
codes_5xx = resp_codes(500, 504)
"""
500 Internal Server Error                   – Generic error when no specific message is available.
501 Not Implemented                         – The server does not support the functionality required.
502 Bad Gateway                             – Received an invalid response from the upstream server.
503 Service Unavailable                     – The server is temporarily unavailable due to overload or maintenance.
504 Gateway Timeout                         – The server didn't receive a timely response from the upstream server.
"""
