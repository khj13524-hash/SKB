#!/bin/bash
cd "$(dirname "$0")"
echo "프록시 서버를 시작합니다... (이 창을 닫으면 서버가 꺼집니다)"
python3 proxy.py
