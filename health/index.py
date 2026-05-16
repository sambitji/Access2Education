def handler(request):
    return {
        "statusCode": 200,
        "body": '{"status": "healthy", "service": "Edu-Platform API"}',
        "headers": {"Content-Type": "application/json"}
    }