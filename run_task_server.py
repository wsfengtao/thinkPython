#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.celery_tasks import celery_server

# run celery task server
if __name__ == "__main__":
    celery_server.start()
