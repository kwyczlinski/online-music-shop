class OrderError(Exception):
    """A general error occured"""
    pass

class OrderNotFoundError(OrderError):
    """Order with given id not found"""
    pass

class ReturnPolicyViolation(OrderError):
    """Order is past the 14-day return window or it is digital"""
    pass