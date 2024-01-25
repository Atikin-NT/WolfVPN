from app import preload

def post_worker_init(worker):
    preload()
