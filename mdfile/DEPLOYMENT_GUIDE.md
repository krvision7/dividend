# 리눅스 서버 배포 가이드 (Dividend Optimizer)

이 문서는 로컬 개발 환경(Windows)에서 개발된 배당 최적화 대시보드를 리눅스 서버(Ubuntu/CentOS 등)로 이전하고 배포하는 절차를 안내합니다.

## 1. 사전 준비 (Prerequisites)

*   **리눅스 서버**: Ubuntu 22.04 LTS 권장 (기타 배포판도 무관)
*   **Python**: 3.10 이상 권장
*   **Git**: 소스 코드 전송용 (또는 SCP 사용)
*   **파일 접근 권한**: `sudo` 권한 필요

## 2. 프로젝트 파일 전송

로컬 PC의 프로젝트 폴더를 서버로 전송해야 합니다. 불필요한 파일(`venv`, `.git`, `__pycache__`)은 제외합니다.

### 방법 A: Git 사용 (권장)
1.  로컬에서 GitHub/GitLab에 푸시합니다.
2.  서버에서 클론합니다.
    ```bash
    git clone <repository_url> dividend_dashboard
    cd dividend_dashboard
    ```

### 방법 B: SCP/SFTP 사용
로컬 터미널(PowerShell/CMD)에서 실행:
```powershell
# 예시: 로컬 폴더를 서버의 홈 디렉토리로 복사
scp -r "c:\Users\krvis\Desktop\00_SERVER\00_2026_01\03_HodoAI\00_dividend" user@your_server_ip:~/dividend_dashboard
```
*주의: `venv` 폴더와 `__pycache__` 폴더는 복사하지 않는 것이 좋습니다. 서버에서 새로 생성해야 합니다.*

## 3. 서버 환경 설정

서버에 접속한 후 다음 명령어를 순서대로 실행합니다.

### 3.1 Python 및 venv 설치
```bash
# Ubuntu 기준
sudo apt update
sudo apt install python3-pip python3-venv -y
```

### 3.2 가상환경 생성 및 패키지 설치
프로젝트 폴더로 이동하여 가상환경을 구성합니다.

```bash
cd ~/dividend_dashboard

# 가상환경 생성 (이름: venv)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```
*`requirements.txt`에 `gunicorn`이 포함되어 있어야 합니다. 없다면 `pip install gunicorn`을 실행하세요.*

## 4. 데이터 로드 (초기화)

서버 환경에서 데이터를 한 번 수집해야 할 수 있습니다. `data` 폴더가 비어있거나 새로 수집하고 싶다면 실행합니다.

```bash
# 데이터 로더 실행 (약 1~2분 소요)
python us_market/dividend/loader.py
```
*이미 `universe_seed.json` 등이 전송되었다면 생략 가능하지만, `data/dividend_universe.json` 파일이 있는지 확인하세요.*

## 5. 서버 실행 (Production 모드)

개발용 서버(`python flask_app.py`) 대신 `Gunicorn`을 사용하여 안정적으로 실행합니다.

### 5.1 Gunicorn으로 테스트 실행
```bash
# 5004 포트로 실행, 워커 4개
gunicorn -w 4 -b 0.0.0.0:5004 flask_app:flask_app
```
브라우저에서 `http://<서버IP>:5004`로 접속하여 잘 뜨는지 확인합니다.
확인 후 `Ctrl+C`로 종료합니다.

### 5.2 백그라운드 서비스 등록 (Systemd) - 권장
서버 재부팅 시 자동 실행되도록 설정합니다.

1.  서비스 파일 생성
    ```bash
    sudo nano /etc/systemd/system/dividend.service
    ```

2.  내용 작성 (경로와 유저명은 본인 환경에 맞춰 수정)
    ```ini
    [Unit]
    Description=Dividend Optimizer Web App
    After=network.target

    [Service]
    User=ubuntu
    Group=ubuntu
    WorkingDirectory=/home/ubuntu/dividend_dashboard
    Environment="PATH=/home/ubuntu/dividend_dashboard/venv/bin"
    # 포트 5004, 워커 4개
    ExecStart=/home/ubuntu/dividend_dashboard/venv/bin/gunicorn -w 4 -b 0.0.0.0:5004 flask_app:flask_app

    [Install]
    WantedBy=multi-user.target
    ```

3.  서비스 시작 및 등록
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start dividend
    sudo systemctl enable dividend
    ```

4.  상태 확인
    ```bash
    sudo systemctl status dividend
    ```

## 6. (선택사항) Nginx 리버스 프록시 설정

80번 포트(http)로 접속하고 싶다면 Nginx를 앞단에 둡니다.

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/dividend
```

내용 작성:
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:5004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

활성화 및 재시작:
```bash
sudo ln -s /etc/nginx/sites-available/dividend /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

이제 `http://<서버IP>` 로 접속 가능합니다.

---

## 문제 해결 (Troubleshooting)

*   **권한 문제**: `Permission denied` 발생 시 폴더 소유권 확인 (`chown -R ubuntu:ubuntu .`)
*   **포트 충돌**: `netstat -tunlp | grep 5004` 로 사용 중인 프로세스 확인
*   **로그 확인**:
    *   Gunicorn 서비스 로그: `sudo journalctl -u dividend -f`
    *   앱 로그: `nohup.out` (nohup 사용 시) 또는 Gunicorn 로그 설정 확인
