from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

def run_with_timeout(func, args=(), kwargs=None, timeout_seconds=120):
    """
    Execute a function with a timeout.
    
    Args:
        func: Function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        timeout_seconds: Maximum execution time in seconds (default: 120)
        
    Returns:
        Function result if completed within timeout
        
    Raises:
        TimeoutError: If function execution exceeds timeout
    """
    if kwargs is None:
        kwargs = {}
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FutureTimeoutError:
            future.cancel()
            raise TimeoutError(f"Operation exceeded {timeout_seconds} seconds timeout")
